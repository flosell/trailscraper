import tempfile

from moto import mock_s3

from tests.test_utils_s3 import file_content, given_a_bucket, given_an_object
from trailscraper.s3_download import _s3_download_recursive


@mock_s3
def test_download_a_single_file_from_prefix():
    given_a_bucket("some-bucket")
    given_an_object("some-bucket", "foo/bar.log", "bar")

    with tempfile.TemporaryDirectory() as dirpath:
        _s3_download_recursive("some-bucket", "foo", dirpath)

        assert file_content(dirpath, "foo/bar.log") == "bar"


@mock_s3
def test_download_multiple_files_from_multiple_nested_dirs():
    given_a_bucket("some-bucket")
    given_an_object("some-bucket", "foo/bar.log", "foo/bar")
    given_an_object("some-bucket", "foo/baz.log", "foo/baz")
    given_an_object("some-bucket", "foo/bar/baz.log", "foo/bar/baz")

    with tempfile.TemporaryDirectory() as dirpath:
        _s3_download_recursive("some-bucket", "foo", dirpath)

        assert file_content(dirpath, "foo/bar.log") == "foo/bar"
        assert file_content(dirpath, "foo/baz.log") == "foo/baz"
        assert file_content(dirpath, "foo/bar/baz.log") == "foo/bar/baz"


