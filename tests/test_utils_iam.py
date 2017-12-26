import fnmatch
import json
import logging

import os
from pkg_resources import resource_filename, Requirement


def all_aws_api_methods():
    botocore_data_dir = resource_filename(Requirement.parse("botocore"), "botocore/data")
    files = [os.path.join(root, file_in_dir) for root, _, files_in_dir in os.walk(botocore_data_dir)
             for file_in_dir in files_in_dir
             if fnmatch.fnmatch(file_in_dir, 'service-*.json')]

    result = []

    for line in files:
        data = json.load(open(line.strip()))
        if 'operations' in data:
            for action in data['operations']:
                result.append(data['metadata']['endpointPrefix']+":"+data['operations'][action]['name'])
        else:
            logging.warn('problem with %s', line.strip())

    return set(result)


def all_iam_permissions_known_in_cloudonaut():
    with open(os.path.join(os.path.dirname(__file__),'iam.json')) as iam_file:
        iam_json = json.loads(iam_file.read())
        return set([d['service']+":"+d['action'] for d in iam_json])


def test_all_aws_api_methods():
    api_methods = all_aws_api_methods()

    assert api_methods != []
    assert "ec2:DescribeInstances" in api_methods
    assert len(api_methods) == len(set(api_methods)), "expected no duplicates"


def test_all_iam_permissions_known_in_cloudonaut():
    permissions = all_iam_permissions_known_in_cloudonaut()

    assert permissions != []
    assert "ec2:DescribeInstances" in permissions
    assert len(permissions) == len(set(permissions)), "expected no duplicates"
