import os

import boto3 as boto3


def file_content(dirpath, key):
    with open(dirpath + os.sep + key) as f:
        return f.read()


def file_does_not_exist(dirpath, key):
    target = dirpath + os.sep + key
    return not os.path.exists(target)


def given_a_bucket(bucket_name):
    s3 = boto3.resource('s3', region_name='us-east-1')
    s3.create_bucket(Bucket=bucket_name)


def given_an_object(bucket, key, body):
    s3 = boto3.resource('s3', region_name='us-east-1')
    s3.Bucket(bucket).put_object(Key=key, Body=body)


def given_a_file(dirpath, key, body):
    target = dirpath + os.sep + key
    if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))

    with open(target, 'w+') as f:
        return f.write(body)
