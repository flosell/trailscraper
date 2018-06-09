from trailscraper.iam import all_known_iam_permissions, Action, known_iam_actions


def test_all_iam_permissions():
    permissions = all_known_iam_permissions()

    assert permissions != []
    assert "ec2:DescribeInstances" in permissions
    assert len(permissions) == len(set(permissions)), "expected no duplicates"


def test_known_iam_action_for_prefix():
    actions = known_iam_actions("acm")
    assert len(actions) == 10
    assert Action("acm","DescribeCertificate") in actions


def test_known_iam_action_for_prefix_does_not_fail_if_action_not_found():
    assert known_iam_actions("something-unknown") == []
