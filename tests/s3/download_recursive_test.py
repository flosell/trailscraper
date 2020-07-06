import sys

if sys.version_info[0] < 3:
    from backports import tempfile
else:
    import tempfile

from moto import mock_s3

from tests.test_utils_s3 import file_content, given_a_bucket, given_an_object, file_does_not_exist
from trailscraper.s3_download import _s3_download_recursive


@mock_s3
def test_download_a_single_file_from_prefix():
    given_a_bucket("some-bucket")
    given_an_object("some-bucket", "foo/bar.log", "bar")

    with tempfile.TemporaryDirectory() as dirpath:
        _s3_download_recursive("some-bucket", ["foo/"], dirpath, 10)

        assert file_content(dirpath, "foo/bar.log") == "bar"


@mock_s3
def test_download_multiple_files_but_only_the_exact_prefix_given():
    given_a_bucket("some-bucket")
    given_an_object("some-bucket", "foo/bar.log", "foo/bar")
    given_an_object("some-bucket", "foo/baz.log", "foo/baz")
    given_an_object("some-bucket", "foo/bar/baz.log", "foo/bar/baz")

    with tempfile.TemporaryDirectory() as dirpath:
        _s3_download_recursive("some-bucket", ["foo/"], dirpath, 10)

        assert file_content(dirpath, "foo/bar.log") == "foo/bar"
        assert file_content(dirpath, "foo/baz.log") == "foo/baz"
        assert file_does_not_exist(dirpath, "foo/bar/baz.log")


@mock_s3
def test_download_files_from_multiple_prefixes():
    given_a_bucket("some-bucket")
    given_an_object("some-bucket", "foo/2017/01/01/foo", "foo")
    given_an_object("some-bucket", "foo/2017/01/02/bar", "bar")
    given_an_object("some-bucket", "foo/2017/01/03/baz", "baz")
    given_an_object("some-bucket", "foo/something", "something")
    given_an_object("some-bucket", "foo/2017/02/01/else", "else")
    given_an_object("some-bucket", "foo/2018/02/01/entirely", "entirely")

    with tempfile.TemporaryDirectory() as dirpath:
        prefixes_to_download = [
            "foo/2017/01/01/",
            "foo/2017/01/02/",
            "foo/2017/01/03/",
        ]
        _s3_download_recursive("some-bucket", prefixes_to_download, dirpath, 10)

        assert file_content(dirpath, "foo/2017/01/01/foo") == "foo"
        assert file_content(dirpath, "foo/2017/01/02/bar") == "bar"
        assert file_content(dirpath, "foo/2017/01/03/baz") == "baz"

        assert file_does_not_exist(dirpath, "foo/something")
        assert file_does_not_exist(dirpath, "foo/2017/02/01/else")
        assert file_does_not_exist(dirpath, "foo/2018/02/01/entirely")
