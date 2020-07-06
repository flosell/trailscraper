"""Functions to download CloudTrail Logs from S3"""
import concurrent.futures
import datetime
import logging
import os
import threading

import boto3
import pytz

from trailscraper.collection_utils import consume


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


def _s3_download_recursive(bucket, prefixes, target_dir, parallelism):
    thread_local = threading.local()
    def get_s3_client():
        if not hasattr(thread_local, "s3_client"):
            thread_local.s3_client = boto3.client('s3')
        return thread_local.s3_client

    def _download_file(key):
        target_file = target_dir + os.sep + key
        logging.info("Downloading %s/%s to %s", bucket, key, target_file)
        # replace with get_object to get rid of extra HEAD call?
        get_s3_client().download_file(bucket, key, target_file)

    def _starts_with_prefix(potential_prefix):
        for prefix in prefixes:
            # potential_prefix always has a trailing slash so this match is good enough:
            if prefix.startswith(potential_prefix):
                return True
        return False

    def _list_files_to_download(current_prefix):
        files_to_download = []
        logging.info("Listing %s", current_prefix)
        paginator = get_s3_client().get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Prefix=current_prefix, Delimiter="/"):
            if result.get('CommonPrefixes') is not None:
                for prefix_result in result.get('CommonPrefixes'):
                    if _starts_with_prefix(prefix_result["Prefix"]):
                        files_to_download.extend(_list_files_to_download(prefix_result["Prefix"]))

            if result.get('Contents') is not None:
                for content in result.get('Contents'):
                    if current_prefix in prefixes:
                        key = content.get('Key')
                        target = target_dir + os.sep + key

                        if not os.path.exists(os.path.dirname(target)):
                            os.makedirs(os.path.dirname(target))

                        if not os.path.exists(target):
                            files_to_download.append(key)
                        else:
                            logging.info("Skipping %s/%s, already exists.", bucket, key)

        return files_to_download

    files_to_download = _list_files_to_download("")

    with concurrent.futures.ThreadPoolExecutor(max_workers=parallelism) as executor:
        results = executor.map(_download_file, files_to_download)
        consume(results) # Ensure we raise exceptions


# pylint: disable=too-many-arguments
def download_cloudtrail_logs(target_dir, bucket, cloudtrail_prefix, org_ids,
                             account_ids, regions, from_date, to_date, parallelism):
    """Downloads cloudtrail logs matching the given arguments to the target dir"""
    prefixes = _s3_key_prefixes(cloudtrail_prefix, org_ids, account_ids, regions, from_date, to_date)
    _s3_download_recursive(bucket, prefixes, target_dir, parallelism)
