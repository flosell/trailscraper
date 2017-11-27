"""Command Line Interface for Trailscraper"""
import logging
import os

import click

from trailscraper.cloudtrail import load_from_dir
from trailscraper.policy_generator import generate_policy_from_records, render_policy
from trailscraper.s3_download import download_cloudtrail_logs


@click.group()
@click.option('--verbose', default=False, is_flag=True)
def root_group(verbose):
    """A command-line tool to get valuable information out of AWS CloudTrail."""
    logger = logging.getLogger()
    if verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('botocore').setLevel(logging.INFO)
        logging.getLogger('s3transfer').setLevel(logging.INFO)


@click.command()
@click.option('--past-days', default=0, help='How many days to look into the past. 0 means today')
@click.option('--bucket', required=True, help='The S3 bucket that contains cloud-trail logs')
@click.option('--prefix', default="", help='Prefix in the S3 bucket (including trailing slash)')
@click.option('--account-id', multiple=True, required=True, help='ID of the account we want to look at')
@click.option('--region', multiple=True, required=True, help='Regions we want to look at')
@click.option('--log-dir', default="~/.trailscraper/logs", type=click.Path(), help='Where to put logfiles')
# pylint: disable=too-many-arguments
def download(past_days, bucket, prefix, account_id, region, log_dir):
    """Downloads CloudTrail Logs from S3."""
    log_dir = os.path.expanduser(log_dir)

    download_cloudtrail_logs(log_dir, bucket, prefix, past_days, account_id, region)


@click.command("generate-policy")
@click.option('--log-dir', default="~/.trailscraper/logs", type=click.Path(), help='Where to put logfiles')
@click.option('--filter-assumed-role-arn', multiple=True,
              help='only consider events from this role (can be used multiple times)')
def generate_policy(log_dir, filter_assumed_role_arn):
    """Generates a policy that allows the events covered in the log-dir"""
    log_dir = os.path.expanduser(log_dir)
    records = load_from_dir(log_dir)

    policy = generate_policy_from_records(records, filter_assumed_role_arn)

    click.echo(render_policy(policy))


root_group.add_command(download)
root_group.add_command(generate_policy)
