from tests.test_utils_testdata import cloudtrail_data, cloudtrail_data_dir
from trailscraper.cloudtrail import _parse_records_from_gzipped_file, load_from_dir
from trailscraper.cloudtrail import Record


def test_parse_records_from_gzipped_file():
    parsed_records = _parse_records_from_gzipped_file(cloudtrail_data("someRecords.json.gz"))
    assert parsed_records == [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
        Record("sts.amazonaws.com", "AssumeRole", ["arn:aws:iam::111111111111:role/someRole"])
    ]


def test_load_all_gzipped_files_from_dir():
    records = load_from_dir(cloudtrail_data_dir())
    assert records == [
        Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations"),
        Record("sts.amazonaws.com", "AssumeRole", ["arn:aws:iam::111111111111:role/someRole"])
    ]
