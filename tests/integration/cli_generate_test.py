import json

from click.testing import CliRunner

from tests.test_utils_testdata import cloudtrail_data_dir, cloudtrail_data
from trailscraper import cli


def test_should_output_an_iam_policy_for_a_set_of_cloudtrail_records_input_from_stdin():
    runner = CliRunner()
    records = open(cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json")).read()
    result = runner.invoke(cli.root_group, args=["generate"], input=records)
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
