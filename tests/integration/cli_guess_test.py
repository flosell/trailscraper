from click.testing import CliRunner

from trailscraper import cli
from trailscraper.iam import PolicyDocument, Statement, Action, parse_policy_document


def test_should_guess_all_matching_statements():
    input_policy = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'DescribeLaunchConfigurations'),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action('sts', 'AssumeRole'),
                ],
                Resource=[
                    "arn:aws:iam::111111111111:role/someRole"
                ]
            )
        ]
    )

    expected_output = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'DescribeLaunchConfigurations'),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'CreateLaunchConfiguration'),
                    Action('autoscaling', 'DeleteLaunchConfiguration'),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action('sts', 'AssumeRole'),
                ],
                Resource=[
                    "arn:aws:iam::111111111111:role/someRole"
                ]
            )
        ]
    )

    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["guess"], input=input_policy.to_json())
    assert result.exit_code == 0
    assert parse_policy_document(result.output) == expected_output


def test_should_guess_only_specific_actions_and_fix_upper_lowercase():
    input_policy = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('ec2', 'DetachVolume'),
                ],
                Resource=["*"]
            ),
        ]
    )

    expected_output = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('ec2', 'DetachVolume'),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action('ec2', 'AttachVolume'),
                    Action('ec2', 'DescribeVolumes'),
                ],
                Resource=["*"]
            ),
        ]
    )

    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["guess", "--only", "Attach", "--only", "describe"], input=input_policy.to_json())
    assert result.exit_code == 0
    assert parse_policy_document(result.output) == expected_output
