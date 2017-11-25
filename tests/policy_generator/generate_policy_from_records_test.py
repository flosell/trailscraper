from awacs.aws import PolicyDocument, Statement, Action

from trailscraper.cloudtrail import Record
from trailscraper.policy_generator import generate_policy_from_records


def test_should_generate_simple_policy():
    records = [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
        Record("sts.amazonaws.com", "AssumeRole")
    ]

    assert generate_policy_from_records(records) == PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'DescribeLaunchConfigurations'),
                    Action('sts', 'AssumeRole'),
                ],
                Resource=["*"]
            )
        ]
    )


def test_should_remove_duplicate_actions():
    records = [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
    ]

    assert generate_policy_from_records(records) == PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'DescribeLaunchConfigurations'),
                ],
                Resource=["*"]
            )
        ]
    )


def test_should_sort_actions_alphabetically():
    records = [
        Record("ec2.amazonaws.com", "DescribeSecurityGroups"),
        Record("rds.amazonaws.com", "ListTagsForResource"),
        Record("ec2.amazonaws.com", "DescribeInstances"),
    ]

    assert generate_policy_from_records(records) == PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action("ec2", "DescribeInstances"),
                    Action("ec2", "DescribeSecurityGroups"),
                    Action("rds", "ListTagsForResource"),
                ],
                Resource=["*"]
            )
        ]
    )


def test_should_group_by_resources():
    records = [
        Record("ec2.amazonaws.com", "DescribeSecurityGroups"),
        Record("rds.amazonaws.com", "ListTagsForResource", ["arn:aws:rds:eu-central-1:111111111111:db:some-db"]),
        Record("ec2.amazonaws.com", "DescribeInstances"),
    ]

    assert generate_policy_from_records(records) == PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action("ec2", "DescribeInstances"),
                    Action("ec2", "DescribeSecurityGroups"),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action("rds", "ListTagsForResource"),
                ],
                Resource=["arn:aws:rds:eu-central-1:111111111111:db:some-db"]
            )
        ]
    )


def test_should_group_by_resources_and_combine_statements_with_same_actions_but_different_resources():
    records = [
        Record("rds.amazonaws.com", "ListTagsForResource", ["arn:aws:rds:eu-central-1:111111111111:db:some-db"]),
        Record("rds.amazonaws.com", "ListTagsForResource", ["arn:aws:rds:eu-central-1:111111111111:db:some-other-db"]),
    ]

    assert generate_policy_from_records(records) == PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action("rds", "ListTagsForResource"),
                ],
                Resource=[
                    "arn:aws:rds:eu-central-1:111111111111:db:some-db",
                    "arn:aws:rds:eu-central-1:111111111111:db:some-other-db",
                ]
            )
        ]
    )
