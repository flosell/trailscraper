import datetime

from trailscraper.cloudtrail import Record
from trailscraper.iam import Statement, Action


def test_should_have_a_string_representation():
    assert str(Record("sts.amazonaws.com", "AssumeRole",
                      resource_arns=["arn:aws:iam::111111111111:role/someRole"],
                      event_time=datetime.datetime(2017, 11, 19, 0, 21, 51))) == \
           "Record(event_source=sts.amazonaws.com event_name=AssumeRole event_time=2017-11-19 00:21:51 " \
           "resource_arns=['arn:aws:iam::111111111111:role/someRole'])"


def test_should_know_about_equality():
    assert Record("sts.amazonaws.com", "AssumeRole") == Record("sts.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole", []) == Record("sts.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole",
                  resource_arns=["arn:aws:iam::111111111111:role/someRole"]) == \
           Record("sts.amazonaws.com", "AssumeRole",
                  resource_arns=["arn:aws:iam::111111111111:role/someRole"])
    assert Record("sts.amazonaws.com", "AssumeRole",
                  assumed_role_arn="arn:aws:iam::111111111111:role/someRole") == \
           Record("sts.amazonaws.com", "AssumeRole",
                  assumed_role_arn="arn:aws:iam::111111111111:role/someRole")

    assert Record("sts.amazonaws.com", "AssumeRole") != Record("sts.amazonaws.com", "AssumeRoles")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("ec2.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("ec2.amazonaws.com", "DescribeInstances")
    assert Record("sts.amazonaws.com", "AssumeRole",
                  resource_arns=["arn:aws:iam::111111111111:role/someRole"]) != \
           Record("sts.amazonaws.com", "AssumeRole", ["arn:aws:iam::222222222222:role/someRole"])
    assert Record("sts.amazonaws.com", "AssumeRole",
                  assumed_role_arn="arn:aws:iam::111111111111:role/someRole") != \
           Record("sts.amazonaws.com", "AssumeRole",
                  assumed_role_arn="arn:aws:iam::111111111111:role/someOtherRole")


def test_should_be_hashable():
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) == hash(Record("sts.amazonaws.com", "AssumeRole"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("sts.amazonaws.com", "AssumeRoles"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("ec2.amazonaws.com", "AssumeRole"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("ec2.amazonaws.com", "DescribeInstances"))


def test_should_convert_into_iam_statement():
    record = Record("autoscaling.amazonaws.com", "DescribeLaunchConfigurations")

    expected_statment = Statement(
        Effect="Allow",
        Action=[
            Action('autoscaling', 'DescribeLaunchConfigurations'),

        ],
        Resource=["*"]
    )

    assert record.to_statement() == expected_statment


def test_should_convert_special_event_sources_properly():
    record = Record("monitoring.amazonaws.com", "DescribeLogStreams")

    expected_statment = Statement(
        Effect="Allow",
        Action=[
            Action("cloudwatch", "DescribeLogStreams"),

        ],
        Resource=["*"]
    )

    assert record.to_statement() == expected_statment


def test_should_convert_special_actions_properly():
    record = Record("lambda", "ListVersionsByFunction20150331")

    expected_statment = Statement(
        Effect="Allow",
        Action=[
            Action("lambda", "ListVersionsByFunction"),

        ],
        Resource=["*"]
    )

    assert record.to_statement() == expected_statment


def test_should_convert_api_gateway_events_properly():
    record = Record("apigateway.amazonaws.com", "CreateRestApi")

    expected_statment = Statement(
        Effect="Allow",
        Action=[
            Action("apigateway", "POST"),

        ],
        Resource=["arn:aws:apigateway:*::/restapis"]
    )

    assert record.to_statement() == expected_statment


def test_should_convert_api_gateway_events_with_parameters_properly():
    record = Record("apigateway.amazonaws.com", "UpdateMethod")

    expected_statment = Statement(
        Effect="Allow",
        Action=[
            Action("apigateway", "PATCH"),

        ],
        Resource=["arn:aws:apigateway:*::/restapis/*/resources/*/methods/*"]
    )

    assert record.to_statement() == expected_statment


def test_should_not_return_statement_for_sts_get_caller_identity_as_it_is_always_allowed():
    assert Record('sts.amazonaws.com', "GetCallerIdentity").to_statement() is None


def test_should_map_normal_event_sources_to_iam_prefix():
    assert Record('autoscaling.amazonaws.com', "something")._source_to_iam_prefix() == 'autoscaling'
    assert Record('sts.amazonaws.com', "something")._source_to_iam_prefix() == 'sts'
    assert Record('ec2.amazonaws.com', "something")._source_to_iam_prefix() == 'ec2'


def test_should_map_special_cases_of_event_sources():
    assert Record('monitoring.amazonaws.com', "something")._source_to_iam_prefix() == 'cloudwatch'


def test_should_map_unknown_sources():
    assert Record('unknown.amazonaws.com', "something")._source_to_iam_prefix() == 'unknown'


def test_should_map_normal_event_names_to_iam_actions():
    assert Record('autoscaling.amazonaws.com', "DescribeAutoScalingGroups")._event_name_to_iam_action() == \
           'DescribeAutoScalingGroups'


def test_should_map_event_names_with_timestamps_to_iam_actions():
    assert Record('lambda', "ListVersionsByFunction20150331")._event_name_to_iam_action() == \
           'ListVersionsByFunction'
    assert Record('lambda', "GetFunctionConfiguration20150331v2")._event_name_to_iam_action() == \
           'GetFunctionConfiguration'
    assert Record('cloudfront', "UpdateDistribution2016_11_25")._event_name_to_iam_action() == \
           'UpdateDistribution'


def test_should_fix_cors():
    assert Record('s3', "PutBucketCors")._event_name_to_iam_action() == \
           'PutBucketCORS'
    assert Record('s3', "DeleteBucketCors")._event_name_to_iam_action() == \
           'PutBucketCORS'
