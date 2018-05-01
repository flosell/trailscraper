import datetime
import logging

from trailscraper import cloudtrail
from trailscraper.cloudtrail import Record, filter_records


def test_should_filter_for_event_time():
    records = [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations", event_time=datetime.datetime(2017, 1, 1)),
        Record("sts.amazonaws.com", "AssumeRole", event_time=datetime.datetime(2017, 6, 6))
    ]

    assert filter_records(records,
                                        from_date=datetime.datetime(2017, 1, 1),
                                        to_date=datetime.datetime(2017, 3, 1)) == \
           [
               Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations",
                      event_time=datetime.datetime(2017, 1, 1)),
           ]


def test_should_warn_if_records_passed_but_filtered_away(caplog):
    records = [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations", event_time=datetime.datetime(2017, 1, 1)),
        Record("sts.amazonaws.com", "AssumeRole", event_time=datetime.datetime(2017, 6, 6))
    ]

    assert filter_records(records,
                                        from_date=datetime.datetime(2010, 1, 1),
                                        to_date=datetime.datetime(2010, 1, 2)) == []

    assert caplog.record_tuples == [
        ('root', logging.WARNING, cloudtrail.ALL_RECORDS_FILTERED),
    ]
