import json

from click.testing import CliRunner

from tests.test_utils_testdata import cloudtrail_data_dir
from trailscraper import cli


def test_should_output_the_timestamp_of_the_last_event():
    runner = CliRunner()
    result = runner.invoke(cli.root_group, args=["last-event-timestamp",
                                                 "--log-dir", cloudtrail_data_dir()
                                                 ])
    assert result.exit_code == 0
    assert result.output == "2017-12-11 15:04:51+00:00\n"

