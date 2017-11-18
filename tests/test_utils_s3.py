import os

import boto3 as boto3


def file_content(dirpath, key):
    with open(dirpath + os.sep + key) as f:
        return f.read()


def given_a_bucket(bucket_name):
    s3 = boto3.resource('s3', region_name='us-east-1')
    s3.create_bucket(Bucket=bucket_name)


def given_an_object(bucket, key, body):
    s3 = boto3.resource('s3', region_name='us-east-1')
    s3.Bucket(bucket).put_object(Key=key, Body=body)
