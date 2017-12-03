from trailscraper.cloudtrail import Record
from trailscraper.iam import Statement, Action


def test_should_have_a_string_representation():
    assert str(Record("sts.amazonaws.com", "AssumeRole",
                      resource_arns=["arn:aws:iam::111111111111:role/someRole"])) == \
           "Record(event_source=sts.amazonaws.com event_name=AssumeRole resource_arns=['arn:aws:iam::111111111111:role/someRole'])"


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


def test_should_map_normal_event_sources_to_iam_prefix():
    assert Record('autoscaling.amazonaws.com', "something")._source_to_iam_prefix() == 'autoscaling'
    assert Record('sts.amazonaws.com', "something")._source_to_iam_prefix() == 'sts'
    assert Record('ec2.amazonaws.com', "something")._source_to_iam_prefix() == 'ec2'


def test_should_map_special_cases():
    assert Record('monitoring.amazonaws.com', "something")._source_to_iam_prefix() == 'cloudwatch'


def test_should_map_unknown_sources():
    assert Record('unknown.amazonaws.com', "something")._source_to_iam_prefix() == 'unknown'
