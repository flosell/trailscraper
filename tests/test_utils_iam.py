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


def all_iam_permissions_known_in_cloudonaut():
    with open(os.path.join(os.path.dirname(__file__), 'iam-actions-from-cloudonaut.json')) as iam_file:
        iam_json = json.loads(iam_file.read())
        return set([d['service'] + ":" + d['action'] for d in iam_json])


def all_iam_permissions_known_in_policy_simulator():
    with open(os.path.join(os.path.dirname(__file__), 'iam-actions-from-policy-sim.txt')) as iam_file:
        return set([line.rstrip('\n') for line in iam_file.readlines()])


def all_known_iam_actions():
    return all_iam_permissions_known_in_policy_simulator().union(all_iam_permissions_known_in_cloudonaut())


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


def test_all_iam_permissions_known_in_policy_simulator():
    permissions = all_iam_permissions_known_in_policy_simulator()

    assert permissions != []
    assert "ec2:DescribeInstances" in permissions
    assert len(permissions) == len(set(permissions)), "expected no duplicates"
