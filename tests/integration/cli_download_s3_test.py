import datetime
import sys

import pytz

if sys.version_info[0] < 3:
    from backports import tempfile
else:
    import tempfile

from click.testing import CliRunner
from moto import mock_s3

from tests.test_utils_s3 import file_content, given_a_bucket, given_an_object, given_a_file
from trailscraper import cli
from trailscraper.s3_download import download_cloudtrail_logs

TEST_LOG_KEY = "some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/file_name.json.gz"
TEST_LOG_KEY_EXISTING = "some-prefix/AWSLogs/000/CloudTrail/some-region-1/2017/01/01/file_name_that_exists.json.gz"


@mock_s3
def test_download_log_files_and_skip_existing_files():
    with tempfile.TemporaryDirectory() as dirpath:
        given_a_bucket("some-bucket")
        given_an_object("some-bucket", TEST_LOG_KEY, "some-file-content")
        given_an_object("some-bucket", TEST_LOG_KEY_EXISTING, "some-file-content")

        given_a_file(dirpath, TEST_LOG_KEY_EXISTING, "some-content-already-existing")

        runner = CliRunner()
        result = runner.invoke(cli.root_group, args=[
            "download",
            "--log-dir", dirpath,
            "--bucket", "some-bucket",
            "--region", "some-region-1",
            "--account-id", "000",
            "--prefix", "some-prefix/",
            "--from", "2017-01-01",
            "--to", "2017-01-01"
        ])
        assert result.exit_code == 0

        assert file_content(dirpath, TEST_LOG_KEY) == "some-file-content"
        assert file_content(dirpath, TEST_LOG_KEY_EXISTING) == "some-content-already-existing"
