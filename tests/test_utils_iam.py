import json
import logging
import os

from trailscraper.boto_service_definitions import boto_service_definition_files


def all_aws_api_methods():
    result = []

    for line in boto_service_definition_files():
        data = json.load(open(line.strip()))
        if 'operations' in data:
            for action in data['operations']:
                result.append(data['metadata']['endpointPrefix'] + ":" + data['operations'][action]['name'])
        else:
            logging.warn('problem with %s', line.strip())

    return set(result)


def all_known_iam_actions():
    with open(os.path.join(os.path.dirname(__file__), 'known-iam-actions.txt')) as iam_file:
        return set([line.rstrip('\n') for line in iam_file.readlines()])


def test_all_aws_api_methods():
    api_methods = all_aws_api_methods()

    assert api_methods != []
    assert "ec2:DescribeInstances" in api_methods
    assert len(api_methods) == len(set(api_methods)), "expected no duplicates"


def test_all_iam_permissions_known_in_cloudonaut():
    permissions = all_known_iam_actions()

    assert permissions != []
    assert "ec2:DescribeInstances" in permissions
    assert len(permissions) == len(set(permissions)), "expected no duplicates"

