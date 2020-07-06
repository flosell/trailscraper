"""Functions to download CloudTrail Logs from S3"""
import datetime
import logging
import os

import boto3
import pytz


def _s3_key_prefix(prefix, date, account_id, region):
    return "{}AWSLogs/{}/CloudTrail/{}/{}/{:02d}/{:02d}/" \
        .format(prefix, account_id, region, date.year, date.month, date.day)

def _s3_key_prefix_for_org_trails(prefix, date, org_id, account_id, region):
    return "{}AWSLogs/{}/{}/CloudTrail/{}/{}/{:02d}/{:02d}/" \
        .format(prefix, org_id, account_id, region, date.year, date.month, date.day)


# pylint: disable=too-many-arguments
def _s3_key_prefixes(prefix, org_ids, account_ids, regions, from_date, to_date):
    delta = to_date.astimezone(pytz.utc) - from_date.astimezone(pytz.utc)

    days = [to_date - datetime.timedelta(days=delta_days) for delta_days in range(delta.days + 1)]
    if org_ids:
        return [_s3_key_prefix_for_org_trails(prefix, day, org_id, account_id, region)
                for org_id in org_ids
                for account_id in account_ids
                for day in days
                for region in regions]

    return [_s3_key_prefix(prefix, day, account_id, region)
            for account_id in account_ids
            for day in days
            for region in regions]


def _s3_download_recursive(bucket, prefixes, target_dir):
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

    def _starts_with_prefix(potential_prefix):
        for prefix in prefixes:
            # potential_prefix always has a trailing slash so this match is good enough:
            if prefix.startswith(potential_prefix):
                return True
        return False

    def _download_dir_again(current_prefix):
        logging.debug("Listing %s", current_prefix)
        paginator = client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Prefix=current_prefix, Delimiter="/"):
            if result.get('CommonPrefixes') is not None:
                for prefix_result in result.get('CommonPrefixes'):
                    if _starts_with_prefix(prefix_result["Prefix"]):
                        _download_dir_again(prefix_result["Prefix"])

            if result.get('Contents') is not None:
                for content in result.get('Contents'):
                    if current_prefix in prefixes:
                        _download_file(content)

    # for prefix in prefixes:
    _download_dir_again("")


# pylint: disable=too-many-arguments
def download_cloudtrail_logs(target_dir, bucket, cloudtrail_prefix, org_ids, account_ids, regions, from_date, to_date):
    """Downloads cloudtrail logs matching the given arguments to the target dir"""
    prefixes = _s3_key_prefixes(cloudtrail_prefix, org_ids, account_ids, regions, from_date, to_date)
    _s3_download_recursive(bucket, prefixes, target_dir)
