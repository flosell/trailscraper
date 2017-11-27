"""Functions to get CloudTrail records from disk"""
import gzip
import json
import logging
import os


class Record():
    """Represents a CloudTrail record"""

    def __init__(self, event_source, event_name, resource_arns=None, assumed_role_arn=None):
        self.event_source = event_source
        self.event_name = event_name
        self.resource_arns = resource_arns or ["*"]
        self.assumed_role_arn = assumed_role_arn

    def __repr__(self):
        return f"Record(event_source={self.event_source} event_name={self.event_name} " \
               f"resource_arns={self.resource_arns})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.event_source == other.event_source and \
                   self.event_name == other.event_name and \
                   self.resource_arns == other.resource_arns and \
                   self.assumed_role_arn == other.assumed_role_arn

        return False

    def __hash__(self):
        return hash((self.event_source,
                     self.event_name,
                     tuple(self.resource_arns),
                     self.assumed_role_arn))

    def __ne__(self, other):
        return not self.__eq__(other)


def _resource_arns(json_record):
    resources = json_record.get('resources', [])
    arns = [resource['ARN'] for resource in resources]
    return arns


def _assumed_role_arn(json_record):
    user_identity = json_record['userIdentity']
    if 'type' in user_identity \
            and user_identity['type'] == 'AssumedRole' \
            and 'sessionContext' in user_identity:
        return user_identity['sessionContext']['sessionIssuer']['arn']
    return None


def _parse_record(json_record):
    try:
        return Record(json_record['eventSource'],
                      json_record['eventName'],
                      resource_arns=_resource_arns(json_record),
                      assumed_role_arn=_assumed_role_arn(json_record))
    except KeyError as error:
        logging.warning("Could not parse %s: %s", json_record, error)
        return None


def _parse_records(json_records):
    parsed_records = [_parse_record(record) for record in json_records]
    return [r for r in parsed_records if r is not None]


def _parse_records_from_gzipped_file(filename):
    """Parses CloudTrail Records from a single file"""
    logging.debug(f"Loading {filename}")

    with gzip.open(filename, 'rb') as file:
        json_data = json.load(file)
        records = json_data['Records']
        return _parse_records(records)


def load_from_dir(log_dir):
    """Loads all CloudTrail Records in a file"""
    records = []
    for root, _, files in os.walk(log_dir):
        for file in files:
            if file.endswith(".json.gz"):
                records.extend(_parse_records_from_gzipped_file(os.path.join(root, file)))

    return records
