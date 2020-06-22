import datetime

import pytz

from tests.test_utils_testdata import cloudtrail_data
from trailscraper.cloudtrail import LogFile, Record


def test_can_parse_logfile_timestamp():
    path = "/logs/AWSLogs/111111111111/CloudTrail/eu-central-1/2017/12/11/" \
           "111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json.gz"

    assert LogFile(path).timestamp() == datetime.datetime(2017,12,11,15,5, tzinfo=pytz.utc)


def test_can_parse_logfile_timestamp_with_zeroes():
    path = "/logs/AWSLogs/111111111111/CloudTrail/eu-central-1/2020/06/03/" \
           "111111111111_CloudTrail_eu-central-1_20200603T0305Z_A6kvhMoVeCsc7v8U.json.gz"

    assert LogFile(path).timestamp() == datetime.datetime(2020,6,3,3,5, tzinfo=pytz.utc)


def test_sees_json_gz_as_valid_filenames():
    path = "/logs/AWSLogs/111111111111/CloudTrail/eu-central-1/2017/12/11/" \
           "111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json.gz"

    assert LogFile(path).has_valid_filename()

def test_sees_json_gz_with_wrong_filename_pattern_as_invalid():
    path = "/logs/AWSLogs/111111111111/CloudTrail/eu-central-1/2017/12/11/" \
           "foo_20171211T1505Z_A6kvhMoVeCsc7v8U.json.gz"

    assert not LogFile(path).has_valid_filename()


def test_does_not_see_something_else_as_valid_filenames():
    path = "/logs/AWSLogs/111111111111/CloudTrail/eu-central-1/2017/12/11/" \
           "111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.txt"

    assert not LogFile(path).has_valid_filename()


def test_parse_records_from_gzipped_file():
    logfile = LogFile(
        cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json.gz"))

    assert logfile.records() == [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations",
               assumed_role_arn="arn:aws:iam::111111111111:role/someRole",
               event_time=datetime.datetime(2017, 12, 11, 15, 1, 51, tzinfo=pytz.utc)),
        Record("sts.amazonaws.com", "AssumeRole",
               resource_arns=["arn:aws:iam::111111111111:role/someRole"],
               event_time=datetime.datetime(2017, 12, 11, 15, 4, 51, tzinfo=pytz.utc))
    ]


def test_parse_records_from_gzipped_file_should_return_empty_for_non_gzipped_files():
    logfile = LogFile(cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json"))
    assert logfile.records() == []
