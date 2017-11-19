"""Functions to download CloudTrail Logs from S3"""
import datetime
import logging
import os

import boto3 as boto3


def _s3_key_prefix(prefix, date, account_id, region):
    return f"{prefix}AWSLogs/{account_id}/CloudTrail/{region}/{date.year}/{date.month:02d}/{date.day:02d}"


def _s3_key_prefixes(prefix, past_days, account_ids, regions):
    now = datetime.datetime.now()
    days = [now - datetime.timedelta(days=delta_days) for delta_days in range(past_days + 1)]
    return [_s3_key_prefix(prefix, day, account_id, region)
            for account_id in account_ids
            for day in days
            for region in regions]


def _s3_download_recursive(bucket, prefix, target_dir):
    client = boto3.client('s3')

    def _download_file(file):
        key = file.get('Key')
        target = target_dir + os.sep + key
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        logging.info(f"Downloading {bucket}/{key} to {target}")
        client.download_file(bucket, key, target)

    def _download_dir(dist):
        paginator = client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Prefix=dist):
            if result.get('CommonPrefixes') is not None:
                for subdir in result.get('CommonPrefixes'):
                    _download_dir(subdir.get('Prefix'))

            if result.get('Contents') is not None:
                for file in result.get('Contents'):
                    _download_file(file)

    _download_dir(prefix)

# pylint: disable=too-many-arguments
def download_cloudtrail_logs(target_dir, bucket, cloudtrail_prefix, past_days, account_ids, regions):
    """Downloads cloudtrail logs matching the given arguments to the target dir"""
    for prefix in _s3_key_prefixes(cloudtrail_prefix, past_days, account_ids, regions):
        logging.debug(f"Downloading logs for {prefix}")
        _s3_download_recursive(bucket, prefix, target_dir)
