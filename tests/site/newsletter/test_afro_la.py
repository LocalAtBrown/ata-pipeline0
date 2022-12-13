import pandas as pd
import pytest

from ata_pipeline0.helpers.fields import FieldSnowplow
from ata_pipeline0.site.names import SiteName
from ata_pipeline0.site.newsletter import AfroLaNewsletterSignupValidator


@pytest.fixture(scope="class")
def nsv() -> AfroLaNewsletterSignupValidator:
    return AfroLaNewsletterSignupValidator()


@pytest.fixture(scope="class")
def event(all_fields, preprocessor_convert_all_field_types) -> pd.Series:
    df = pd.DataFrame(
        [
            [
                "2022-11-03 05:39:13.16",
                "697",
                "4",
                "7292d425-2424-4b00-9894-b31a87a770bd",
                "768",
                "1366",
                "2bba4051-c7f9-46cd-90bc-9b869a5fe187",
                "submit_form",
                "156f6713-4722-49cc-8335-721742f66525",
                "https://www.afrolanews.org/",
                "/subscribe",
                None,
                "unknown",
                None,
                SiteName.AFRO_LA,
                None,
                None,
                "{'formId': 'FORM', 'formClasses': ['group', 'w-full', 'rounded-wt', 'bg-transparent', 'shadow-none', 'sm:shadow-md'], 'elements': [{'name': 'ref', 'value': '', 'nodeName': 'INPUT', 'type': 'text'}, {'name': 'redirect_path', 'value': '/', 'nodeName': 'INPUT', 'type': 'hidden'}, {'name': 'double_opt', 'value': 'true', 'nodeName': 'INPUT', 'type': 'hidden'}, {'name': 'origin', 'value': '/subscribe', 'nodeName': 'INPUT', 'type': 'hidden'}, {'name': 'visit_token', 'value': '004abfd4-ea3e-4246-87a4-83d0e153d383', 'nodeName': 'INPUT', 'type': 'text'}, {'name': 'email', 'value': 'dummyemail@dummydomain.com', 'nodeName': 'INPUT', 'type': 'email'}]}",
                "Mozilla/5.0 (X11; CrOS x86_64 14816.131.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            ]
        ],
        columns=all_fields,
    )

    return preprocessor_convert_all_field_types(df).iloc[0]


@pytest.mark.unit
class TestAfroLaNewsletterSignupValidators:
    def test_is_in_newsletter_page_true(self, nsv, event) -> None:
        assert nsv.is_in_newsletter_page(event)

    def test_is_in_newsletter_page_false(self, nsv, event) -> None:
        event = event.copy()
        event[FieldSnowplow.PAGE_URLPATH] = "/"
        assert nsv.is_in_newsletter_page(event) is False