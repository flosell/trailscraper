"""Functions responsible for generating a policy from a set of CloudTrail Records"""
from functools import reduce
from itertools import groupby

import toolz as toolz

from trailscraper.iam import PolicyDocument, Statement


def _combine_statements_with_the_same_actions(statements):
    combined_statements = []
    key_function = lambda statement: tuple(statement.Action)

    for _, group in toolz.groupby(key_function, statements).items():
        combined_statements.append(reduce(Statement.merge, group))
    return combined_statements

def generate_policy_from_records(records, arns_to_filter_for=None):
    """Generates a policy from a set of records"""

    if arns_to_filter_for is None:
        arns_to_filter_for = []

    statements = [
        record.to_statement()
        for record in records if (record.assumed_role_arn in arns_to_filter_for) or (len(arns_to_filter_for) == 0)
    ]

    combined_statements = _combine_statements_with_the_same_actions(
        _combine_statements_with_the_same_resources(statements))

    return PolicyDocument(
        Version="2012-10-17",
        Statement=combined_statements,
    )


def _combine_statements_with_the_same_resources(statements):
    combined_statements = []
    key_function = lambda statement: statement.Resource
    for _, group in groupby(sorted(statements, key=key_function), key=key_function):
        combined_statements.append(reduce(Statement.merge, group))
    return combined_statements


def render_policy(policy):
    """Renders a given policy as an IAM compatible JSON-String"""
    return policy.to_json()
