"""Command Line Interface for Trailscraper"""
import json
import logging
import os
import time

import click

import trailscraper
from trailscraper import time_utils, policy_generator
from trailscraper.cloudtrail import filter_records, \
    parse_records
from trailscraper.guess import guess_statements
from trailscraper.iam import parse_policy_document
from trailscraper.record_sources.cloudtrail_api_record_source import CloudTrailAPIRecordSource
from trailscraper.record_sources.local_directory_record_source import LocalDirectoryRecordSource
from trailscraper.s3_download import download_cloudtrail_logs


@click.group()
@click.version_option(version=trailscraper.__version__)
@click.option('--verbose', default=False, is_flag=True)
def root_group(verbose):
    """A command-line tool to get valuable information out of AWS CloudTrail."""
    logger = logging.getLogger()
    if verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('botocore').setLevel(logging.INFO)
        logging.getLogger('s3transfer').setLevel(logging.INFO)


@click.command()
@click.option('--bucket', required=True,
              help='The S3 bucket that contains cloud-trail logs')
@click.option('--prefix', default="",
              help='Prefix in the S3 bucket (including trailing slash)')
@click.option('--org-id', multiple=True, default=[],
              help='ID of the organisation we want to look at. Defaults to empty for non-organisational trails')
@click.option('--account-id', multiple=True, required=True,
              help='ID of the account we want to look at')
@click.option('--region', multiple=True, required=True,
              help='Regions we want to look at')
@click.option('--log-dir', default="~/.trailscraper/logs", type=click.Path(),
              help='Where to put logfiles')
@click.option('--from', 'from_s', default="one day ago", type=click.STRING,
              help='Start date, e.g. "2017-01-01" or "-1days". Defaults to "one day ago".')
@click.option('--to', 'to_s', default="now", type=click.STRING,
              help='End date, e.g. "2017-01-01" or "now". Defaults to "now".')
@click.option('--wait', default=False, is_flag=True,
              help='Wait until events after the specified timeframe are found.')
@click.option('--parallelism', default=10, type=click.INT,
              help='How many files to download in parallel')
# pylint: disable=too-many-arguments
def download(bucket, prefix, org_id, account_id, region, log_dir, from_s, to_s, wait, parallelism):
    """Downloads CloudTrail Logs from S3."""
    log_dir = os.path.expanduser(log_dir)

    from_date = time_utils.parse_human_readable_time(from_s)
    to_date = time_utils.parse_human_readable_time(to_s)

    download_cloudtrail_logs(log_dir, bucket, prefix, org_id, account_id, region, from_date, to_date, parallelism)

    if wait:
        last_timestamp = LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir()
        while last_timestamp <= to_date:
            click.echo("CloudTrail logs haven't caught up to " + str(to_date) + " yet. " +
                       "Most recent timestamp: " + str(last_timestamp.astimezone(to_date.tzinfo)) + ". " +
                       "Trying again in 60sec.")

            time.sleep(60 * 1)

            download_cloudtrail_logs(log_dir, bucket, prefix, org_id,
                                     account_id, region, from_date, to_date, parallelism)
            last_timestamp = LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir()


@click.command("select")
@click.option('--log-dir', default="~/.trailscraper/logs", type=click.Path(),
              help='Where to put logfiles')
@click.option('--filter-assumed-role-arn', multiple=True,
              help='only consider events from this role (can be used multiple times)')
@click.option('--use-cloudtrail-api', is_flag=True, default=False,
              help='Pull Events from CloudtrailAPI instead of log-dir')
@click.option('--from', 'from_s', default="1970-01-01", type=click.STRING,
              help='Start date, e.g. "2017-01-01" or "-1days"')
@click.option('--to', 'to_s', default="now", type=click.STRING,
              help='End date, e.g. "2017-01-01" or "now"')
def select(log_dir, filter_assumed_role_arn, use_cloudtrail_api, from_s, to_s):
    """Finds all CloudTrail records matching the given filters and prints them."""
    log_dir = os.path.expanduser(log_dir)
    from_date = time_utils.parse_human_readable_time(from_s)
    to_date = time_utils.parse_human_readable_time(to_s)

    if use_cloudtrail_api:
        records = CloudTrailAPIRecordSource().load_from_api(from_date, to_date)
    else:
        records = LocalDirectoryRecordSource(log_dir).load_from_dir(from_date, to_date)

    filtered_records = filter_records(records, filter_assumed_role_arn, from_date, to_date)

    filtered_records_as_json = [record.raw_source for record in filtered_records]

    click.echo(json.dumps({"Records": filtered_records_as_json}))


@click.command("generate")
def generate():
    """Generates a policy that allows the events passed in through STDIN"""
    stdin = click.get_text_stream('stdin')
    records = parse_records(json.load(stdin)['Records'])

    policy = policy_generator.generate_policy(records)
    click.echo(policy.to_json())


@click.command("guess")
@click.option("--only", multiple=True,
              help='Only guess actions with the given prefix, e.g. Describe (can be passed multiple times)')
def guess(only):
    """Extend a policy passed in through STDIN by guessing related actions"""
    stdin = click.get_text_stream('stdin')
    policy = parse_policy_document(stdin)

    allowed_prefixes = [s.title() for s in only]

    policy = guess_statements(policy, allowed_prefixes)
    click.echo(policy.to_json())


@click.command("last-event-timestamp")
@click.option('--log-dir', default="~/.trailscraper/logs", type=click.Path(),
              help='Where to put logfiles')
def last_event_timestamp(log_dir):
    """Print the most recent cloudtrail event timestamp"""
    log_dir = os.path.expanduser(log_dir)
    click.echo(LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir())


root_group.add_command(download)
root_group.add_command(select)
root_group.add_command(generate)
root_group.add_command(guess)
root_group.add_command(last_event_timestamp)
