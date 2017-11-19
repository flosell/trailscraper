"""Functions responsible for generating a policy from a set of CloudTrail Records"""
from awacs.aws import  Action, Allow, PolicyDocument, Principal, Statement


def generate_policy_from_records(records):
    """Generates a policy from a set of records"""
    return {}


def render_policy(policy):
    """Renders a given policy as an IAM compatible JSON-String"""
    policy_document = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action("sts","AssumeRole"),
                    Action("autoscaling","DescribeLaunchConfigurations")
                ],
                Resource=["*"]
            )
        ]
    )
    return policy_document.to_json()
