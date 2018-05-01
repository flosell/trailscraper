from trailscraper.cloudtrail import Record
from trailscraper.iam import PolicyDocument, Statement, Action
from trailscraper.policy_generator import generate_policy


def test_should_generate_simple_policy():
    records = [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
        Record("sts.amazonaws.com", "AssumeRole")
    ]

    assert generate_policy(records) == PolicyDocument(
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

    assert generate_policy(records) == PolicyDocument(
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


def test_should_allow_events_that_dont_map_to_statement():
    records = [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
        Record("sts.amazonaws.com", "GetCallerIdentity")
    ]

    assert generate_policy(records) == PolicyDocument(
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

    assert generate_policy(records) == PolicyDocument(
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

    assert generate_policy(records) == PolicyDocument(
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

    assert generate_policy(records) == PolicyDocument(
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


def test_should_group_by_action_and_resource_independent_of_order():
    records = [
        Record("rds.amazonaws.com", "ListTagsForResource", ["arn:aws:rds:eu-central-1:111111111111:db:some-db"]),
        Record("rds.amazonaws.com", "SomethingDifferent", ["arn:aws:rds:eu-central-1:111111111111:db:a-third-db"]),
        Record("rds.amazonaws.com", "ListTagsForResource", ["arn:aws:rds:eu-central-1:111111111111:db:some-other-db"]),
    ]

    expected = PolicyDocument(
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
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action("rds", "SomethingDifferent"),
                ],
                Resource=[
                    "arn:aws:rds:eu-central-1:111111111111:db:a-third-db",
                ]
            ),
        ])
    actual = generate_policy(records)
    assert actual == expected
