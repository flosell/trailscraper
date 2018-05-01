import json

from click.testing import CliRunner

from tests.test_utils_testdata import cloudtrail_data_dir, cloudtrail_data
from trailscraper import cli

def test_should_output_all_cloudtrail_records_in_data_dir():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["select",
                                                 "--log-dir", cloudtrail_data_dir(),
                                                 ])
    expected_json = json.load(open(cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json")))

    assert result.exit_code == 0
    assert json.loads(result.output) == expected_json


def test_should_output_cloudrail_records_filtered_by_role_arn():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["select",
                                                 "--log-dir", cloudtrail_data_dir(),
                                                 "--filter-assumed-role-arn", "arn:aws:iam::111111111111:role/someRole"
                                                 ])
    expected_json = json.load(open(cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json")))
    expected_json['Records'].pop(1)
    assert result.exit_code == 0
    assert json.loads(result.output) == expected_json


def test_should_output_cloudrail_records_filtered_by_timeframe():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["select",
                                                 "--log-dir", cloudtrail_data_dir(),
                                                 "--from", "2017-12-11 15:00:00Z",
                                                 "--to", "2017-12-11 15:02:00Z"])
    expected_json = json.load(open(cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json")))
    expected_json['Records'].pop(1) # TODO: this test should use a different record to distinguish between filtering arns and timeframes
    assert result.exit_code == 0
    assert json.loads(result.output) == expected_json
