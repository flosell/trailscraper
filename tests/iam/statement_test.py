import pytest

from trailscraper.iam import Statement, Action


def test_should_merge_two_identical_statements():
    statement1 = Statement(
        Effect="Allow",
        Action=[
            Action("some-service", "some-action"),
        ],
        Resource=[
            "some-resource",
        ]
    )
    statement2 = Statement(
        Effect="Allow",
        Action=[
            Action("some-service", "some-action"),
        ],
        Resource=[
            "some-resource",
        ]
    )

    assert statement1.merge(statement2) == statement1
    assert statement2.merge(statement1) == statement2


def test_should_merge_two_statements_with_different_actions_and_resources():
    statement1 = Statement(
        Effect="Allow",
        Action=[
            Action("some-service", "some-action"),
        ],
        Resource=[
            "some-resource",
        ]
    )
    statement2 = Statement(
        Effect="Allow",
        Action=[
            Action("some-service", "some-other-action"),
        ],
        Resource=[
            "some-resource",
            "some-other-resource",
        ]
    )

    merged = Statement(
        Effect="Allow",
        Action=[
            Action("some-service", "some-action"),
            Action("some-service", "some-other-action"),
        ],
        Resource=[
            "some-other-resource",
            "some-resource",
        ]
    )

    assert statement1.merge(statement2) == merged


def test_should_merge_deny_statments():
    statement1 = Statement(
        Effect="Deny",
        Action=[Action("some-service", "some-action")],
        Resource=["*"])

    statement2 = Statement(
        Effect="Deny",
        Action=[Action("some-service", "some-other-action")],
        Resource=["*"])

    merged = Statement(
        Effect="Deny",
        Action=[
            Action("some-service", "some-action"),
            Action("some-service", "some-other-action"),
        ],
        Resource=["*"])

    assert statement1.merge(statement2) == merged


def test_should_fail_if_effects_arent_the_same():
    statement1 = Statement(
        Effect="Allow",
        Action=[],
        Resource=[])
    statement2 = Statement(
        Effect="Deny",
        Action=[],
        Resource=[])

    with pytest.raises(ValueError) as e:
        statement1.merge(statement2)

    assert str(e.value) == "Trying to combine two statements with differing effects: Allow Deny"


def test_should_order_by_effect_first():
    statement1 = Statement(
        Effect="Allow",
        Action=[],
        Resource=[])
    statement2 = Statement(
        Effect="Deny",
        Action=[],
        Resource=[])

    assert statement1 < statement2
    assert not statement1 > statement2


def test_should_order_by_action_list_second():
    statement1 = Statement(
        Effect="Allow",
        Action=[Action("ec2", "DescribeInstances")],
        Resource=[])
    statement2 = Statement(
        Effect="Deny",
        Action=[Action("iam", "PassRole")],
        Resource=[])

    assert statement1 < statement2
    assert not statement1 > statement2


def test_should_order_by_resource_list_third():
    statement1 = Statement(
        Effect="Allow",
        Action=[],
        Resource=["a"])

    statement2 = Statement(
        Effect="Allow",
        Action=[],
        Resource=["b"])

    assert statement1 < statement2
    assert not statement1 > statement2

def test_same_statements_have_the_same_order():
    statement1 = Statement(
        Effect="Allow",
        Action=[],
        Resource=["a"])

    statement2 = Statement(
        Effect="Allow",
        Action=[],
        Resource=["a"])

    assert not statement1 < statement2
    assert not statement1 > statement2
    assert statement1 == statement2

