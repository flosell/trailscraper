import datetime

import pytz

from trailscraper.s3_download import _s3_key_prefixes


def test_should_generate_prefixes_for_one_day():
    assert _s3_key_prefixes(prefix="some-prefix/",
                            org_ids=[],
                            account_ids=["000"],
                            regions=["some-region-1"],
                            from_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            to_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc)) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/"]


def test_should_generate_prefixes_for_multiple_accounts_on_one_day():
    assert _s3_key_prefixes(prefix="some-prefix/",
                            from_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            to_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            org_ids=[],
                            account_ids=["000", "111"],
                            regions=["some-region-1"]) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/",
            "some-prefix/AWSLogs/111/CloudTrail/some-region-1/2017/01/01/"]


def test_should_generate_prefixes_for_one_day_when_datetime_contains_time():
    assert _s3_key_prefixes(prefix="some-prefix/",
                            org_ids=[],
                            account_ids=["000"],
                            regions=["some-region-1"],
                            from_date=datetime.datetime(2017, 1, 1, 10, 0, 0, tzinfo=pytz.utc),
                            to_date=datetime.datetime(2017, 1, 1, 11, 0, 0, tzinfo=pytz.utc)) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/"]


def test_should_generate_prefixes_for_multiple_days():
    assert _s3_key_prefixes(prefix="some-prefix/",
                            org_ids=[],
                            account_ids=["000"],
                            regions=["some-region-1"],
                            from_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            to_date=datetime.datetime(2017, 1, 2, tzinfo=pytz.utc)) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/02/",
            "some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/", ]


def test_should_generate_prefixes_for_regions():
    assert _s3_key_prefixes(prefix="some-prefix/",
                            from_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            to_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            org_ids=[],
                            account_ids=["000"],
                            regions=["some-region-1", "some-region-2"]) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/",
            "some-prefix/AWSLogs/000/CloudTrail/some-region-2/2017/01/01/"]


def test_should_generate_prefixes_one_organisation():
    assert _s3_key_prefixes(prefix="some-prefix/",
                            org_ids=["o-s0mething"],
                            account_ids=["000"],
                            regions=["some-region-1"],
                            from_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
                            to_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc)) == \
           ["some-prefix/AWSLogs/o-s0mething/000/CloudTrail/some-region-1/2017/01/01/"]
