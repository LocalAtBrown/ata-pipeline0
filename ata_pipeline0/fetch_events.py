import gzip
import itertools
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Optional

import pandas as pd
from mypy_boto3_s3.service_resource import ObjectSummary, S3ServiceResource
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef

from ata_pipeline0.helpers.logging import logging
from ata_pipeline0.helpers.site import SiteName

logger = logging.getLogger(__name__)


def fetch_events(
    s3_resource: S3ServiceResource,
    site_name: SiteName,
    num_concurrent_downloads: int,
    timestamps: Optional[List[datetime]] = None,
    object_key: Optional[str] = None,
) -> pd.DataFrame:
    """
    Given config inputs, including a site's bucket name and a list of date-hour
    timestamps, fetches corresponding S3 Snowplow event files and returns them
    as a single DataFrame.

    Requires an S3ServiceResource as a parameter; here's how to create it:
    >>> import boto3
    >>> s3_resource = boto3.resource("s3")
    """
    # Grab S3 bucket
    bucket = s3_resource.Bucket(f"lnl-snowplow-{site_name}")

    # Get S3 objects to fetch
    if object_key:
        object_summaries = itertools.chain(*[bucket.objects.filter(Prefix=object_key)])
    elif timestamps:
        object_summaries_by_timestamp = [
            bucket.objects.filter(Prefix=f"enriched/good/{ts.strftime('%Y/%m/%d/%H')}") for ts in timestamps
        ]
        object_summaries = itertools.chain(*object_summaries_by_timestamp)
    else:
        raise ValueError("Need to provide either timestamps or object_key to fetch_events")

    # Spread fetching tasks over a number of CPU threads. Until aioboto3 is
    # thoroughly documented and isn't a pain to work with (or until boto3
    # is asyncio-friendly), multithreading is a decent alternative and much
    # (2x, using max_workers=os.cpu_count() + 4) faster than sequential fetching
    #
    # Fetching all data (even gzipped) from the get-go might incur significant
    # memory footprint, but this is a simple start
    with ThreadPoolExecutor(max_workers=num_concurrent_downloads) as executor:
        dfs = executor.map(_fetch_decompress_parse, object_summaries)

    # Append an empty DataFrame at the beginning in case len(dfs) == 0, in which
    # case using dfs alone causes pd.concat throws an error
    df = pd.concat([pd.DataFrame(), *dfs])

    logger.info(f"Fetched DataFrame shape: {df.shape}")

    return df


def _fetch_decompress_parse(object_summary: ObjectSummary) -> pd.DataFrame:
    response = _fetch_object(object_summary)
    data = _decompress_object(response)
    df = _parse_object(data)
    return df


def _fetch_object(object_summary: ObjectSummary) -> GetObjectOutputTypeDef:
    return object_summary.get()


def _decompress_object(object_response: GetObjectOutputTypeDef) -> bytes:
    data = object_response["Body"].read()
    # Assuming all objects are .gz files
    data = gzip.decompress(data)
    return data


def _parse_object(object_data: bytes) -> pd.DataFrame:
    data = object_data.decode("utf-8").strip().split("\n")
    data = [json.loads(row) for row in data]
    # Setting everything as str because we'll do our own typecasting later
    return pd.DataFrame(data, dtype=str)
