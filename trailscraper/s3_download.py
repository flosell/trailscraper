"""Functions to download CloudTrail Logs from S3"""
import datetime
import logging
import os

import boto3 as boto3


def _s3_key_prefix(prefix, date, account_id, region):
    return "{}AWSLogs/{}/CloudTrail/{}/{}/{:02d}/{:02d}" \
        .format(prefix, account_id, region, date.year, date.month, date.day)


def _s3_key_prefixes(prefix, account_ids, regions, from_date, to_date):
    delta = to_date - from_date

    days = [to_date - datetime.timedelta(days=delta_days) for delta_days in range(delta.days + 1)]
    return [_s3_key_prefix(prefix, day, account_id, region)
            for account_id in account_ids
            for day in days
            for region in regions]


def _s3_download_recursive(bucket, prefix, target_dir):
    client = boto3.client('s3')

    def _download_file(object_info):
        key = object_info.get('Key')
        target = target_dir + os.sep + key
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))

        if not os.path.exists(target):
            logging.info("Downloading %s/%s to %s", bucket, key, target)
            client.download_file(bucket, key, target)
        else:
            logging.info("Skipping %s/%s, already exists.", bucket, key)


    def _download_dir(dist):
        paginator = client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Prefix=dist):
            if result.get('CommonPrefixes') is not None:
                for subdir in result.get('CommonPrefixes'):
                    _download_dir(subdir.get('Prefix'))

            if result.get('Contents') is not None:
                for content in result.get('Contents'):
                    _download_file(content)

    _download_dir(prefix)


# pylint: disable=too-many-arguments
def download_cloudtrail_logs(target_dir, bucket, cloudtrail_prefix, account_ids, regions, from_date, to_date):
    """Downloads cloudtrail logs matching the given arguments to the target dir"""
    for prefix in _s3_key_prefixes(cloudtrail_prefix, account_ids, regions, from_date, to_date):
        logging.debug("Downloading logs for %s", prefix)
        _s3_download_recursive(bucket, prefix, target_dir)
