import json

from click.testing import CliRunner

from tests.test_utils_testdata import cloudtrail_data_dir
from trailscraper import cli


def test_should_output_an_iam_policy_for_a_set_of_cloudtrail_records():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["generate-policy", "--log-dir", cloudtrail_data_dir()])
    assert result.exit_code == 0
    assert json.loads(result.output) == json.loads('''\
{
    "Statement": [
        {
            "Action": [
                "autoscaling:DescribeLaunchConfigurations"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "sts:AssumeRole"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:iam::111111111111:role/someRole"
            ]
        }
    ],
    "Version": "2012-10-17"
}
''')


def test_should_filter_for_assumed_role_arn():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["generate-policy", "--log-dir", cloudtrail_data_dir(),
                                                 "--filter-assumed-role-arn",
                                                 "arn:aws:iam::111111111111:role/someRole"])
    assert json.loads(result.output) == json.loads('''\
{
    "Statement": [
        {
            "Action": [
                "autoscaling:DescribeLaunchConfigurations"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ],
    "Version": "2012-10-17"
}
''')
    assert result.exit_code == 0
