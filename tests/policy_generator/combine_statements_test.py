import pytest
from awacs.aws import Statement, Action

from trailscraper.policy_generator import _combine_statements


def test_should_combine_two_identical_statements():
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

    assert _combine_statements(statement1, statement2) == statement1
    assert _combine_statements(statement1, statement2) == statement2


def test_should_combine_two_statements_with_different_actions_and_resources():
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

    combined = Statement(
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

    assert _combine_statements(statement1, statement2) == combined


def test_should_combine_deny_statments():
    statement1 = Statement(
        Effect="Deny",
        Action=[Action("some-service", "some-action")],
        Resource=["*"])

    statement2 = Statement(
        Effect="Deny",
        Action=[Action("some-service", "some-other-action")],
        Resource=["*"])

    combined = Statement(
        Effect="Deny",
        Action=[
            Action("some-service", "some-action"),
            Action("some-service", "some-other-action"),
        ],
        Resource=["*"])

    assert _combine_statements(statement1, statement2) == combined


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
        _combine_statements(statement1, statement2)

    assert str(e.value) == "Trying to combine two statements with differing effects: Allow Deny"
