"""Functions responsible for generating a policy from a set of CloudTrail Records"""
from itertools import groupby

from awacs.aws import Action, PolicyDocument, Statement


def _source_to_iam_prefix(event_source):
    special_cases = {'monitoring.amazonaws.com': 'cloudwatch'}
    default_case = event_source.split('.')[0]

    return special_cases.get(event_source, default_case)


def _combine_actions_with_same_resource(statements):
    statements = list(statements)
    actions = [action for statement in statements for action in statement.Action]
    return Statement(
        Effect="Allow",
        Action=list(sorted(set(actions), key=lambda action: action.JSONrepr())),
        Resource=sorted(statements[0].Resource)
    )


def _combine_resources_with_the_same_actions(statement):
    statement_list = list(statement)
    resources = [action for statement in statement_list for action in statement.Resource]
    return Statement(
        Effect="Allow",
        Action=statement_list[0].Action,
        Resource=resources
    )


def _combine_statements_with_the_same_actions(statements):
    combined_statements = []
    key_function = lambda statement: statement.Action
    # pylint: disable=fixme
    # FIXME: groupby expects sorted statements, otherwise it might not group properly...
    for _, group in groupby(statements, key=key_function):
        combined_statements.append(_combine_resources_with_the_same_actions(group))
    return combined_statements


def generate_policy_from_records(records):
    """Generates a policy from a set of records"""

    statements = [
        Statement(
            Effect="Allow",
            Action=[Action(_source_to_iam_prefix(record.event_source), record.event_name)],
            Resource=sorted(record.resource_arns)
        ) for record in records
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
        combined_statements.append(_combine_actions_with_same_resource(group))
    return combined_statements


def render_policy(policy):
    """Renders a given policy as an IAM compatible JSON-String"""
    return policy.to_json()
