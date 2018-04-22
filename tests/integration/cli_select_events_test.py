import json

from click.testing import CliRunner

from tests.test_utils_testdata import cloudtrail_data_dir, cloudtrail_data
from trailscraper import cli

def test_should_output_all_cloudtrail_records_in_data_dir():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["select",
                                                 "--log-dir", cloudtrail_data_dir(),
                                                 # TODO: ideally, the default should be no filtering at all
                                                 "--from", "2016-12-10",
                                                 "--to", "2017-12-20",
                                                 ])
    expected_json = json.load(open(cloudtrail_data("111111111111_CloudTrail_eu-central-1_20171211T1505Z_A6kvhMoVeCsc7v8U.json")))

    assert result.exit_code == 0
    assert json.loads(result.output) == expected_json
