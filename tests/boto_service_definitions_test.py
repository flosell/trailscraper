from trailscraper.boto_service_definitions import boto_operation_definition, \
    boto_service_definition


def test_should_find_most_recent_service_definition_file():
    assert boto_service_definition("ec2")['metadata']['apiVersion'] == '2016-11-15'

def test_should_find_operation_definitions():
    assert boto_operation_definition("apigateway", "UpdateApiKey") == {
        "name": "UpdateApiKey",
        "http": {
            "method": "PATCH",
            "requestUri": "/apikeys/{api_Key}"
        },
        "input": {"shape": "UpdateApiKeyRequest"},
        "output": {"shape": "ApiKey"},
        "errors": [
            {"shape": "BadRequestException"},
            {"shape": "ConflictException"},
            {"shape": "LimitExceededException"},
            {"shape": "NotFoundException"},
            {"shape": "UnauthorizedException"},
            {"shape": "TooManyRequestsException"}
        ],
        "documentation": "<p>Changes information about an ApiKey resource.</p>"
    }
