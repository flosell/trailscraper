import datetime

import sys

import pytz

if sys.version_info[0] < 3:
    from backports import tempfile
else:
    import tempfile

from moto import mock_s3

from tests.test_utils_s3 import file_content, given_a_bucket, given_an_object, given_a_file
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

        download_cloudtrail_logs(
            target_dir=dirpath,
            bucket="some-bucket",
            cloudtrail_prefix="some-prefix/",
            from_date=datetime.datetime(2017, 1, 1, tzinfo=pytz.utc),
            to_date=datetime.datetime(2018, 1, 1, tzinfo=pytz.utc),
            account_ids=["000"],
            org_ids=[],
            regions=["some-region-1"],
            parallelism=10,
        )

        assert file_content(dirpath, TEST_LOG_KEY) == "some-file-content"
        assert file_content(dirpath, TEST_LOG_KEY_EXISTING) == "some-content-already-existing"
