import datetime

import pytz

from tests.test_utils_testdata import cloudtrail_data_dir
from trailscraper.cloudtrail import Record
from trailscraper.record_sources.local_directory_record_source import LocalDirectoryRecordSource


def test_load_gzipped_files_in_timeframe_from_dir():
    records = LocalDirectoryRecordSource(cloudtrail_data_dir()).load_from_dir(
                            datetime.datetime(2017, 12, 1, tzinfo=pytz.utc),
                            datetime.datetime(2017, 12, 12, tzinfo=pytz.utc))
    assert records == [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations",
               assumed_role_arn="arn:aws:iam::111111111111:role/someRole",
               # "2017-12-11T15:01:51Z"
               event_time=datetime.datetime(2017, 12, 11, 15, 1, 51, tzinfo=pytz.utc)),
        Record("sts.amazonaws.com", "AssumeRole",
               resource_arns=["arn:aws:iam::111111111111:role/someRole"],
               event_time=datetime.datetime(2017, 12, 11, 15, 4, 51, tzinfo=pytz.utc))
    ]


def test_load_gzipped_files_including_those_that_were_delivered_only_an_hour_after_the_event_time_we_are_looking_for():
    records = LocalDirectoryRecordSource(cloudtrail_data_dir()).load_from_dir(
                            datetime.datetime(2017, 12, 11, 0, 0, tzinfo=pytz.utc),
                            datetime.datetime(2017, 12, 11, 14, 5, tzinfo=pytz.utc))
    assert records == [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations",
               assumed_role_arn="arn:aws:iam::111111111111:role/someRole",
               # "2017-12-11T15:01:51Z"
               event_time=datetime.datetime(2017, 12, 11, 15, 1, 51, tzinfo=pytz.utc)),
        Record("sts.amazonaws.com", "AssumeRole",
               resource_arns=["arn:aws:iam::111111111111:role/someRole"],
               event_time=datetime.datetime(2017, 12, 11, 15, 4, 51, tzinfo=pytz.utc))
    ]


def test_load_no_gzipped_files_outsite_timeframe_from_dir():
    records = LocalDirectoryRecordSource(cloudtrail_data_dir()).load_from_dir(
                            datetime.datetime(2016, 12, 1, tzinfo=pytz.utc),
                            datetime.datetime(2016, 12, 12, tzinfo=pytz.utc))
    assert records == []

