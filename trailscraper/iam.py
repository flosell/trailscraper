import json
import os
import re
from typing import List, Dict, Union

import six
from toolz import pipe
from toolz.curried import groupby as groupbyz
from toolz.curried import map as mapz

BASE_ACTION_PREFIXES = ["Describe", "Create", "Delete", "Update", "Detach", "Attach", "List", "Put", "Get"]

class BaseElement:
    """Base Class for all IAM Policy classes"""

    def json_repr(self) -> Union[str, dict]:
        """JSON representation of the class"""
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.json_repr() == other.json_repr()

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(self.json_repr())

    def __repr__(self) -> str:
        return str(self.json_repr())


class Action(BaseElement):
    """Action in an IAM Policy."""

    def __init__(self, prefix: str, action: str):
        self.prefix = prefix
        self.action = action

    def json_repr(self) -> str:
        return ':'.join([self.prefix, self.action])

    def _base_action(self) -> str:
        without_prefix = self.action
        for prefix in BASE_ACTION_PREFIXES:
            without_prefix = re.sub(prefix, "", without_prefix)

        without_plural = re.sub(r"s$", "", without_prefix)
        return without_plural

    def matching_actions(self, allowed_prefixes: List[str] = None) -> List['Action']:
        """Return matching actions for this Action."""
        if allowed_prefixes is None:
            allowed_prefixes = BASE_ACTION_PREFIXES

        base_action = self._base_action()
        potential_matches = [
            Action(prefix=self.prefix, action=f"{action_prefix}{base_action}{'s' if plural else ''}")
            for action_prefix in allowed_prefixes
            for plural in [False, True]
        ]

        return [pm for pm in potential_matches if pm in known_iam_actions(self.prefix) and pm != self]


class Statement(BaseElement):
    """Statement in an IAM Policy."""

    def __init__(self, actions: List[Action], effect: str, resources: List[str]):
        self.actions = actions
        self.effect = effect
        self.resources = resources

    def json_repr(self) -> dict:
        return {
            'Action': [action.json_repr() for action in self.actions],
            'Effect': self.effect,
            'Resource': self.resources,
        }

    def merge(self, other: 'Statement') -> 'Statement':
        """Merge two statements into one."""
        if self.effect != other.effect:
            raise StatementMergeError(f"Cannot merge statements with different effects: {self.effect} vs {other.effect}")

        actions = list(sorted(set(self.actions + other.actions), key=lambda action: action.json_repr()))
        resources = list(sorted(set(self.resources + other.resources)))

        return Statement(actions=actions, effect=self.effect, resources=resources)

    def __lt__(self, other: 'Statement') -> bool:
        if self.effect != other.effect:
            return self.effect < other.effect
        if self.actions != other.actions:
            return "-".join(a.json_repr() for a in self.actions) < "-".join(a.json_repr() for a in other.actions)

        return "".join(self.resources) < "".join(other.resources)


class PolicyDocument(BaseElement):
    """IAM Policy Document."""

    def __init__(self, statements: List[Statement], version: str = "2012-10-17"):
        self.version = version
        self.statements = statements

    def json_repr(self) -> dict:
        return {
            'Version': self.version,
            'Statement': [statement.json_repr() for statement in self.statements]
        }

    def to_json(self) -> str:
        """Render object into IAM Policy JSON"""
        return json.dumps(self.json_repr(), cls=IAMJSONEncoder, indent=4, sort_keys=True)


class IAMJSONEncoder(json.JSONEncoder):
    """JSON Encoder using the json_repr functions"""

    def default(self, o):  # pylint: disable=method-hidden
        if hasattr(o, 'json_repr'):
            return o.json_repr()
        return super().default(o)


def _parse_action(action: str) -> Action:
    parts = action.split(":")
    return Action(parts[0], parts[1])


def _parse_statement(statement: dict) -> Statement:
    return Statement(
        actions=[_parse_action(action) for action in statement['Action']],
        effect=statement['Effect'],
        resources=statement['Resource']
    )


def _parse_statements(json_data: Union[List[dict], dict]) -> List[Statement]:
    if isinstance(json_data, dict):
    # jsonData could also be dict, aka one statement; similar things happen in the rest of the policy pylint: disable=fixme
    # https://github.com/flosell/iam-policy-json-to-terraform/blob/fafc231/converter/decode.go#L12-L22
        return [_parse_statement(json_data)]
    
    # Handle multiple statements case
    return [_parse_statement(statement) for statement in json_data]


def parse_policy_document(stream: Union[str, bytes]) -> PolicyDocument:
    """Parse a stream of JSON data to a PolicyDocument object"""
    if isinstance(stream, six.string_types):
        json_dict = json.loads(stream)
    else:
        json_dict = json.load(stream)

    return PolicyDocument(statements=_parse_statements(json_dict['Statement']), version=json_dict.get('Version'))


def all_known_iam_permissions() -> set:
    """Return a set of all known IAM actions."""
    with open(os.path.join(os.path.dirname(__file__), 'known-iam-actions.txt'), encoding="UTF-8") as iam_file:
        return {line.strip() for line in iam_file}


def known_iam_actions(prefix: str) -> List[Action]:
    """Return known IAM actions for a prefix."""
    knowledge = pipe(all_known_iam_permissions(),
                     mapz(_parse_action),
                     groupbyz(lambda x: x.prefix))

    return knowledge.get(prefix, [])
