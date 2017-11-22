"""Functions to get CloudTrail records from disk"""
import gzip
import json
import logging
import os


class Record():
    """Represents a CloudTrail record"""

    def __init__(self, event_source, event_name, resource_arns=None):
        self.event_source = event_source
        self.event_name = event_name
        self.resource_arns = resource_arns or ["*"]

    def __repr__(self):
        return f"Record(event_source={self.event_source} event_name={self.event_name} " \
               f"resource_arns={self.resource_arns})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.event_source == other.event_source and \
                   self.event_name == other.event_name and \
                   self.resource_arns == other.resource_arns

        return False

    def __hash__(self):
        return hash((self.event_source, self.event_name, tuple(self.resource_arns)))

    def __ne__(self, other):
        return not self.__eq__(other)


def _resource_arns(json_record):
    resources = json_record.get('resources', [])
    arns = [resource['ARN'] for resource in resources]
    return arns


def _mk_record(json_record):
    return Record(json_record['eventSource'],
                  json_record['eventName'],
                  _resource_arns(json_record))


def _parse_records_from_gzipped_file(filename):
    """Parses CloudTrail Records from a single file"""
    logging.debug(f"Loading {filename}")

    with gzip.open(filename, 'rb') as file:
        json_data = json.load(file)
        return [_mk_record(record) for record in json_data['Records']]


def load_from_dir(log_dir):
    """Loads all CloudTrail Records in a file"""
    records = []
    for root, _, files in os.walk(log_dir):
        for file in files:
            if file.endswith(".json.gz"):
                records.extend(_parse_records_from_gzipped_file(os.path.join(root, file)))

    return records
