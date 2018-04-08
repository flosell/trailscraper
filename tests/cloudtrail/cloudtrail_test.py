import datetime

import pytz

from tests.test_utils_testdata import cloudtrail_data_dir
from trailscraper.cloudtrail import Record
from trailscraper.cloudtrail import load_from_dir, _parse_record, \
    _parse_records


def test_load_gzipped_files_in_timeframe_from_dir():
    records = load_from_dir(cloudtrail_data_dir(),
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
    records = load_from_dir(cloudtrail_data_dir(),
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
    records = load_from_dir(cloudtrail_data_dir(),
                            datetime.datetime(2016, 12, 1, tzinfo=pytz.utc),
                            datetime.datetime(2016, 12, 12, tzinfo=pytz.utc))
    assert records == []


def test_parse_record_should_be_able_to_cope_with_missing_type():
    assert _parse_record({'userIdentity': {'accountId': '111111111111'},
                          'eventSource': 'kms.amazonaws.com',
                          'eventName': 'DeleteKey',
                          'eventTime': '2017-11-19T00:21:51Z'}) == \
           Record('kms.amazonaws.com', 'DeleteKey',
                  event_time=datetime.datetime(2017, 11, 19, 0, 21, 51, tzinfo=pytz.utc))


def test_parse_record_should_be_able_to_cope_with_missing_session_context_in_assumed_role():
    assert _parse_record({'eventVersion': '1.05',
                          'userIdentity': {'type': 'AssumedRole', 'principalId': 'some-key:some-user',
                                           'arn': 'arn:aws:sts::111111111111:assumed-role/some-role/some-user',
                                           'accountId': '111111111111'},
                          'eventSource': 'signin.amazonaws.com',
                          'eventTime': '2017-11-19T00:21:51Z',
                          'eventName': 'RenewRole'}) == \
           Record('signin.amazonaws.com', 'RenewRole',
                  event_time=datetime.datetime(2017, 11, 19, 0, 21, 51, tzinfo=pytz.utc))


def test_parse_records_should_ignore_records_that_cant_be_parsed():
    assert _parse_records([{},
                           {'eventVersion': '1.05',
                            'userIdentity': {'type': 'SomeType'},
                            'eventSource': 'someSource',
                            'eventName': 'SomeEvent',
                            'eventTime': '2017-11-19T00:21:51Z'}]) == \
           [Record('someSource', 'SomeEvent',
                   event_time=datetime.datetime(2017, 11, 19, 0, 21, 51, tzinfo=pytz.utc))]
