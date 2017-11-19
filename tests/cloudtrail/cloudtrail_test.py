import os

from trailscraper.cloudtrail import parse_records_from_gzipped_file


def test_parse_records_from_gzipped_file():
    parsed_records = parse_records_from_gzipped_file(_testdata_file("someRecords.json.gz"))
    assert parsed_records == []


def _testdata_file(filename):
    os.path.join(os.path.dirname(__file__), 'data', filename)
