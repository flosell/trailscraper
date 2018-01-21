import os

from pkg_resources import resource_filename, Requirement

from trailscraper.boto_service_definitions import service_definition_file, operation_definition


def test_should_find_most_recent_service_definition_file_for_ec2():
    botocore_data_dir = resource_filename(Requirement.parse("botocore"), "botocore/data")
    expected_filename = os.path.join(botocore_data_dir, "ec2", "2016-11-15", "service-2.json")

    assert service_definition_file("ec2") == expected_filename


def test_should_find_operation_definitions():
    assert operation_definition("apigateway", "UpdateApiKey") == {
        "name": "UpdateApiKey",
        "http": {
            "method": "PATCH",
            "requestUri": "/apikeys/{api_Key}"
        },
        "input": {"shape": "UpdateApiKeyRequest"},
        "output": {"shape": "ApiKey"},
        "errors": [
            {"shape": "UnauthorizedException"},
            {"shape": "NotFoundException"},
            {"shape": "BadRequestException"},
            {"shape": "TooManyRequestsException"},
            {"shape": "ConflictException"}
        ],
        "documentation": "<p>Changes information about an <a>ApiKey</a> resource.</p>"
    }
