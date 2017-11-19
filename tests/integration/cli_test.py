from click.testing import CliRunner

from tests.test_utils_testdata import cloudtrail_data_dir
from trailscraper import cli


def test_should_output_help_message_by_default():
    runner = CliRunner()
    result = runner.invoke(cli.root_group)
    assert result.exit_code == 0
    assert 'Usage:' in result.output


def test_should_output_an_iam_policy_for_a_set_of_cloudtrail_records():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["generate-policy", "--log-dir", cloudtrail_data_dir()])
    assert result.exit_code == 0
    assert result.output == '''\
{
    "Statement": [
        {
            "Action": [
                "autoscaling:DescribeLaunchConfigurations",
                "sts:AssumeRole"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ],
    "Version": "2012-10-17"
}
'''
