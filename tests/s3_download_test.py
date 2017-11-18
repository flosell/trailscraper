from freezegun import freeze_time

from trailscraper.s3_download import _s3_key_prefixes


@freeze_time("2017-01-01")
def test_should_generate_a_single_prefix_for_today():
    assert _s3_key_prefixes(prefix="some-prefix",
                            past_days=0,
                            account_ids=["111"],
                            regions=["some-region-1"]) == \
           ["some-prefix/AWSLogs/111/CloudTrail/some-region-1/2017/01/01"]


@freeze_time("2017-01-01")
def test_should_generate_prefixes_for_multiple_accounts_today():
    assert _s3_key_prefixes(prefix="some-prefix",
                            past_days=0,
                            account_ids=["000", "111"],
                            regions=["some-region-1"]) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01",
            "some-prefix/AWSLogs/111/CloudTrail/some-region-1/2017/01/01"]


@freeze_time("2017-01-01")
def test_should_generate_prefixes_for_regions():
    assert _s3_key_prefixes(prefix="some-prefix",
                            past_days=0,
                            account_ids=["000"],
                            regions=["some-region-1","some-region-2"]) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01",
            "some-prefix/AWSLogs/000/CloudTrail/some-region-2/2017/01/01"]


@freeze_time("2017-01-01")
def test_should_generate_prefixes_for_multiple_days_in_the_past():
    assert _s3_key_prefixes(prefix="some-prefix",
                            past_days=2,
                            account_ids=["000"],
                            regions=["some-region-1"]) == \
           ["some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01",
            "some-prefix/AWSLogs/000/CloudTrail/some-region-1/2016/12/31",
            "some-prefix/AWSLogs/000/CloudTrail/some-region-1/2016/12/30", ]
