from trailscraper.cloudtrail import Record


def test_should_have_a_string_representation():
    assert str(Record("sts.amazonaws.com", "AssumeRole")) == \
           "Record(event_source=sts.amazonaws.com event_name=AssumeRole)"


def test_should_know_about_equality():
    assert Record("sts.amazonaws.com", "AssumeRole") == Record("sts.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("sts.amazonaws.com", "AssumeRoles")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("ec2.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("ec2.amazonaws.com", "DescribeInstances")


def test_should_be_hashable():
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) == hash(Record("sts.amazonaws.com", "AssumeRole"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("sts.amazonaws.com", "AssumeRoles"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("ec2.amazonaws.com", "AssumeRole"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("ec2.amazonaws.com", "DescribeInstances"))

