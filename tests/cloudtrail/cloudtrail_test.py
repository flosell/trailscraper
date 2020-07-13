import datetime

import pytz

from trailscraper.cloudtrail import Record
from trailscraper.cloudtrail import _parse_record, \
    parse_records


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


def test_parse_record_should_be_able_to_cope_with_missing_arn_in_resource():
    assert _parse_record({'eventVersion': '1.05',
                          'eventTime': '2018-05-15T02:18:43Z',
                          'eventName': 'ListObjects',
                          'eventSource': 's3.amazonaws.com',
                          'userIdentity': {'type': 'AssumedRole', 'principalId': 'some-key:some-user',
                                           'arn': 'arn:aws:sts::111111111111:assumed-role/some-role/some-user',
                                           'accountId': '111111111111'},
                          'resources': [
                              {'ARNPrefix': 'arn:aws:s3:::some-bucket/env:/',
                               'type': 'AWS::S3::Object'},
                              {'type': 'AWS::S3::Bucket',
                               'ARN': 'arn:aws:s3:::some-bucket',
                               'accountId': '201571571865'}],
                          }) == \
           Record('s3.amazonaws.com', 'ListObjects',
                  event_time=datetime.datetime(2018, 5, 15, 2, 18, 43, tzinfo=pytz.utc),
                  resource_arns=["arn:aws:s3:::some-bucket"])


def test_parse_records_should_ignore_records_that_cant_be_parsed():
    assert parse_records([{},
                          {'eventVersion': '1.05',
                           'userIdentity': {'type': 'SomeType'},
                           'eventSource': 'someSource',
                           'eventName': 'SomeEvent',
                           'eventTime': '2017-11-19T00:21:51Z'}]) == \
           [Record('someSource', 'SomeEvent',
                   event_time=datetime.datetime(2017, 11, 19, 0, 21, 51, tzinfo=pytz.utc))]
