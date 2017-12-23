"""Functions to get CloudTrail records from disk"""
import datetime
import gzip
import json
import logging
import os

import boto3
from trailscraper.iam import Statement, Action


class Record(object):
    """Represents a CloudTrail record"""

    # pylint: disable=too-many-arguments
    def __init__(self, event_source, event_name, resource_arns=None, assumed_role_arn=None, event_time=None):
        self.event_source = event_source
        self.event_name = event_name
        self.event_time = event_time
        self.resource_arns = resource_arns or ["*"]
        self.assumed_role_arn = assumed_role_arn

    def __repr__(self):

        return "Record(event_source={} event_name={} event_time={} resource_arns={})"\
            .format(self.event_source, self.event_name, self.event_time, self.resource_arns)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.event_source == other.event_source and \
                   self.event_name == other.event_name and \
                   self.event_time == other.event_time and \
                   self.resource_arns == other.resource_arns and \
                   self.assumed_role_arn == other.assumed_role_arn

        return False

    def __hash__(self):
        return hash((self.event_source,
                     self.event_name,
                     self.event_time,
                     tuple(self.resource_arns),
                     self.assumed_role_arn))

    def __ne__(self, other):
        return not self.__eq__(other)

    def _source_to_iam_prefix(self):
        special_cases = {'monitoring.amazonaws.com': 'cloudwatch'}
        default_case = self.event_source.split('.')[0]

        return special_cases.get(self.event_source, default_case)

    def to_statement(self):
        """Converts record into a matching IAM Policy Statement"""
        return Statement(
            Effect="Allow",
            Action=[Action(self._source_to_iam_prefix(), self.event_name)],
            Resource=sorted(self.resource_arns)
        )


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
                      event_time=datetime.datetime.strptime(json_record['eventTime'], "%Y-%m-%dT%H:%M:%SZ"),
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
    logging.debug("Loading "+filename)

    try:
        with gzip.open(filename, 'rt') as unzipped:
            json_data = json.load(unzipped)
            records = json_data['Records']
            return _parse_records(records)
    except OSError as error:
        logging.warning("Could not load %s: %s", filename, error)
        return []


def load_from_dir(log_dir):
    """Loads all CloudTrail Records in a file"""
    records = []
    for root, _, logfiles in os.walk(log_dir):
        for logfile in logfiles:
            if logfile.endswith(".json.gz"):
                records.extend(_parse_records_from_gzipped_file(os.path.join(root, logfile)))

    return records


def load_from_api(from_date, to_date):
    """Loads the last 10 hours of cloudtrail events from the API"""
    client = boto3.client('cloudtrail')
    paginator = client.get_paginator('lookup_events')
    response_iterator = paginator.paginate(
        StartTime=from_date,
        EndTime=to_date,
    )
    records = []
    for response in response_iterator:
        for event in response['Events']:
            records.append(_parse_record(json.loads(event['CloudTrailEvent'])))

    return records
