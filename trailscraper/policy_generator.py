"""Functions responsible for generating a policy from a set of CloudTrail Records"""

import toolz as toolz
from toolz import pipe
from toolz.curried import filter as filterz
from toolz.curried import map as mapz

from trailscraper.cloudtrail import Record
from trailscraper.iam import PolicyDocument, Statement


def _combine_statements_by(key):
    def _result(statements):
        key_function = lambda statement: tuple(key(statement))
        return list(toolz.reduceby(key_function, Statement.merge, statements).values())

    return _result


def _by_role_arns(arns_to_filter_for):
    if arns_to_filter_for is None:
        arns_to_filter_for = []

    return lambda record: (record.assumed_role_arn in arns_to_filter_for) or (len(arns_to_filter_for) == 0)


def generate_policy_from_records(records, arns_to_filter_for=None):
    """Generates a policy from a set of records"""

    statements = pipe(records,
                      filterz(_by_role_arns(arns_to_filter_for)),
                      mapz(Record.to_statement),
                      _combine_statements_by(lambda statement: statement.Resource),
                      _combine_statements_by(lambda statement: statement.Action))

    return PolicyDocument(
        Version="2012-10-17",
        Statement=statements,
    )
