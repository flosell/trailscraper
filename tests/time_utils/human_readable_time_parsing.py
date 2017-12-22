import datetime

import pytz

from freezegun import freeze_time

from trailscraper.time_utils import parse_human_readable_time


def test_should_parse_full_dates():
    assert parse_human_readable_time("2017-12-22") == \
           datetime.datetime(2017, 12, 22, 0, 0, 0)


def test_should_parse_full_datetimes():
    assert parse_human_readable_time("2017-12-22 10:11:12") == \
           datetime.datetime(2017, 12, 22, 10, 11, 12)

@freeze_time("2010-11-12 13:14:15")
def test_should_parse_human_readable_current_time():
    assert parse_human_readable_time("now").astimezone(pytz.utc) == \
           datetime.datetime(2010,11,12,13,14,15,tzinfo=pytz.utc)

@freeze_time("2010-11-12 13:14:15")
def test_should_parse_human_readable_relative_times():
    assert parse_human_readable_time("one hour ago").astimezone(pytz.utc) == \
           datetime.datetime(2010,11,12,12,14,15,tzinfo=pytz.utc)
    assert parse_human_readable_time("in 10 minutes").astimezone(pytz.utc) == \
           datetime.datetime(2010,11,12,13,24,15,tzinfo=pytz.utc)

    assert parse_human_readable_time("-1 hour").astimezone(pytz.utc) == \
           datetime.datetime(2010,11,12,12,14,15,tzinfo=pytz.utc)
    assert parse_human_readable_time("-1 day").astimezone(pytz.utc) == \
           datetime.datetime(2010,11,11,13,14,15,tzinfo=pytz.utc)
    assert parse_human_readable_time("-10 minutes").astimezone(pytz.utc) == \
           datetime.datetime(2010,11,12,13,4,15,tzinfo=pytz.utc)
