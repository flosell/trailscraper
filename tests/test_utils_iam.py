import json
import logging

from trailscraper.boto_service_definitions import boto_service_definition_files


def all_aws_api_methods():
    result = []

    for line in boto_service_definition_files():
        data = json.load(open(line.strip()))
        if 'operations' in data:
            for action in data['operations']:
                result.append(data['metadata']['endpointPrefix'] + ":" + data['operations'][action]['name'])
        else:
            logging.warning('problem with %s', line.strip())

    return set(result)


def test_all_aws_api_methods():
    api_methods = all_aws_api_methods()

    assert api_methods != []
    assert "ec2:DescribeInstances" in api_methods
    assert len(api_methods) == len(set(api_methods)), "expected no duplicates"

