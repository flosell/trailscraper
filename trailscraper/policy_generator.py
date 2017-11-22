"""Functions responsible for generating a policy from a set of CloudTrail Records"""

from awacs.aws import Action, PolicyDocument, Statement


def _source_to_iam_prefix(event_source):
    special_cases = {'monitoring.amazonaws.com': 'cloudwatch'}
    default_case = event_source.split('.')[0]

    return special_cases.get(event_source, default_case)


def generate_policy_from_records(records):
    """Generates a policy from a set of records"""
    actions = [Action(_source_to_iam_prefix(record.event_source), record.event_name) for record in records]
    resources = [arn for record in records for arn in record.resource_arns]

    return PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=sorted(set(actions), key=lambda x: x.prefix + x.action),
                Resource=sorted(set(resources))
            )
        ]
    )


def render_policy(policy):
    """Renders a given policy as an IAM compatible JSON-String"""
    return policy.to_json()
