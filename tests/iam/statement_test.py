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
