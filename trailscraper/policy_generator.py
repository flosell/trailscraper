"""Functions responsible for generating a policy from a set of CloudTrail Records"""
import datetime
import logging

import pytz
import toolz as toolz
from toolz import pipe
from toolz.curried import filter as filterz
from toolz.curried import map as mapz
from toolz.curried import sorted as sortedz

from trailscraper.cloudtrail import Record, filter_records
from trailscraper.iam import PolicyDocument, Statement

NO_RECORDS_WARNING = "No cloudtrail records found in input! Did you download the right logfiles? " \
                     "It might take about 15 minutes for events to turn up in CloudTrail logs."

ALL_RECORDS_FILTERED = "No records matching your criteria found! Did you use the right filters?"


def _combine_statements_by(key):
    def _result(statements):
        key_function = lambda statement: tuple(key(statement))
        return list(toolz.reduceby(key_function, Statement.merge, statements).values())

    return _result


def generate_policy_from_records(records,
                                 arns_to_filter_for=None,
                                 from_date=datetime.datetime(1970, 1, 1, tzinfo=pytz.utc),
                                 to_date=datetime.datetime.now(tz=pytz.utc)):
    """Generates a policy from a set of records that matches the given conditions"""
    if not records:
        logging.warning(NO_RECORDS_WARNING)

    filtered_records = list(filter_records(records, arns_to_filter_for, from_date, to_date))

    if len(filtered_records) == 0 and records:
        logging.warning(ALL_RECORDS_FILTERED)

    return generate_policy(filtered_records)


def generate_policy(selected_records):
    """Generates a policy from a set of records"""
    statements = pipe(selected_records,
                      mapz(Record.to_statement),
                      filterz(lambda statement: statement is not None),
                      _combine_statements_by(lambda statement: statement.Resource),
                      _combine_statements_by(lambda statement: statement.Action),
                      sortedz())

    return PolicyDocument(
        Version="2012-10-17",
        Statement=statements,
    )
