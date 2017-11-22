from trailscraper.cloudtrail import Record


def test_should_have_a_string_representation():
    assert str(Record("sts.amazonaws.com", "AssumeRole",["arn:aws:iam::111111111111:role/someRole"])) == \
           "Record(event_source=sts.amazonaws.com event_name=AssumeRole resource_arns=['arn:aws:iam::111111111111:role/someRole'])"


def test_should_know_about_equality():
    assert Record("sts.amazonaws.com", "AssumeRole") == Record("sts.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole",[]) == Record("sts.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole",["arn:aws:iam::111111111111:role/someRole"]) == \
           Record("sts.amazonaws.com", "AssumeRole",["arn:aws:iam::111111111111:role/someRole"])
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("sts.amazonaws.com", "AssumeRoles")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("ec2.amazonaws.com", "AssumeRole")
    assert Record("sts.amazonaws.com", "AssumeRole") != Record("ec2.amazonaws.com", "DescribeInstances")
    assert Record("sts.amazonaws.com", "AssumeRole", ["arn:aws:iam::111111111111:role/someRole"]) != \
           Record("sts.amazonaws.com", "AssumeRole", ["arn:aws:iam::222222222222:role/someRole"])


def test_should_be_hashable():
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) == hash(Record("sts.amazonaws.com", "AssumeRole"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("sts.amazonaws.com", "AssumeRoles"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("ec2.amazonaws.com", "AssumeRole"))
    assert hash(Record("sts.amazonaws.com", "AssumeRole")) != hash(Record("ec2.amazonaws.com", "DescribeInstances"))

