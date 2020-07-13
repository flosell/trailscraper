"""Module for CloudTrailAPIRecordSource"""
import json

import boto3

from trailscraper.cloudtrail import _parse_record


class CloudTrailAPIRecordSource():
    """Class to represent CloudTrail records from the CloudTrail lookup_events API"""
    def __init__(self):
        self._client = boto3.client('cloudtrail')

    # pylint: disable=no-self-use
    def load_from_api(self, from_date, to_date):
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
