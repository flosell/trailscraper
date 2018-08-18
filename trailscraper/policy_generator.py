"""Functions responsible for generating a policy from a set of CloudTrail Records"""

import toolz
from toolz import pipe
from toolz.curried import filter as filterz
from toolz.curried import map as mapz
from toolz.curried import sorted as sortedz

from trailscraper.cloudtrail import Record
from trailscraper.iam import PolicyDocument, Statement


def _combine_statements_by(key):
    def _result(statements):
        key_function = lambda statement: tuple(key(statement))
        return list(toolz.reduceby(key_function, Statement.merge, statements).values())

    return _result


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
