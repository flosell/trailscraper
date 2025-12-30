import logging

from trailscraper.boto_service_definitions import boto_services, boto_service_definition


def all_aws_api_methods():
    result = []
    for service in boto_services():
        data = boto_service_definition(service)

        if 'operations' in data:
            for action in data['operations']:
                result.append(data['metadata']['endpointPrefix'] + ":" + data['operations'][action]['name'])
        else:
            logging.warning('problem with %s', service.strip())

    return set(result)


def test_all_aws_api_methods():
    api_methods = all_aws_api_methods()

    assert api_methods != []
    assert "ec2:DescribeInstances" in api_methods
    assert len(api_methods) == len(set(api_methods)), "expected no duplicates"

