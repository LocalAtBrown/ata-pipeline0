import pandas as pd
from ata_db_models.models import Event
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from ata_pipeline0.helpers.logging import logging

logger = logging.getLogger(__name__)


def write_events(df: pd.DataFrame, session_factory: sessionmaker) -> int:
    """
    Writes preprocessed events to database.

    This function accepts a `sessionmaker`, which is a factory for session
    objects, given an engine. A `sessionmaker` can be created like so:
    >>> session_factory = sessionmaker(engine)
    """
    data = df.to_dict(orient="records")

    if data:

        # Create statement to bulk-insert event rows
        # Insert.on_conflict_do_nothing skips through events whose [event_id, site_name]
        # composite key already exists in the DB
        statement = insert(Event).values(data).on_conflict_do_nothing(index_elements=[Event.site_name, Event.event_id])

        # Wrap execution within a begin-commit-rollback block
        # (see: https://docs.sqlalchemy.org/en/14/orm/session_basics.html#framing-out-a-begin-commit-rollback-block)
        # TODO: Once sqlalchemy-stubs catches up to SQLAlchemy 1.4, remove the type: ignore comment below
        # (see: https://github.com/dropbox/sqlalchemy-stubs/blob/ed9611114925f4b2aea42401217c0eacb1a564e1/sqlalchemy-stubs/orm/session.pyi#L102)
        with session_factory.begin() as session:  # type: ignore
            result = session.execute(statement)

        # Count number of rows/events inserted
        num_rows_inserted = result.rowcount

        # Log message
        logger.info(
            f"Inserted {num_rows_inserted} rows into the {Event.__name__} table. "
            + f"Skipped {df.shape[0] - num_rows_inserted} rows whose event ID-site name composite key already exists."
        )

        return num_rows_inserted
    else:
        logger.info("No rows to insert.")
        return 0
