"""Classes to deal with IAM Policies"""
import json
import os

import re

import six
from toolz import pipe
from toolz.curried import groupby as groupbyz
from toolz.curried import map as mapz

BASE_ACTION_PREFIXES = ["Describe", "Create", "Delete", "Update", "Detach", "Attach", "List", "Put", "Get", ]


class BaseElement:
    """Base Class for all IAM Policy classes"""

    def json_repr(self):
        """JSON representation of the class"""
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.json_repr() == other.json_repr()

        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.json_repr())

    def __repr__(self):
        return str(self.json_repr())


class Action(BaseElement):
    """Action in an IAM Policy."""

    def __init__(self, prefix, action):
        self.action = action
        self.prefix = prefix

    def json_repr(self):
        return ':'.join([self.prefix, self.action])

    def _base_action(self):
        without_prefix = self.action
        for prefix in BASE_ACTION_PREFIXES:
            without_prefix = re.sub(prefix, "", without_prefix)

        without_plural = re.sub(r"s$", "", without_prefix)

        return without_plural

    def matching_actions(self, allowed_prefixes):
        """Return a matching create action for this Action"""

        if not allowed_prefixes:
            allowed_prefixes = BASE_ACTION_PREFIXES

        potential_matches = [Action(prefix=self.prefix, action=action_prefix + self._base_action())
                             for action_prefix in allowed_prefixes]

        potential_matches += [Action(prefix=self.prefix, action=action_prefix + self._base_action() + "s")
                              for action_prefix in allowed_prefixes]

        return [potential_match
                for potential_match in potential_matches
                if potential_match in known_iam_actions(self.prefix) and potential_match != self]



class Statement(BaseElement):
    """Statement in an IAM Policy."""

    def __init__(self, Action, Effect, Resource):  # pylint: disable=redefined-outer-name
        self.Action = Action  # pylint: disable=invalid-name
        self.Effect = Effect  # pylint: disable=invalid-name
        self.Resource = Resource  # pylint: disable=invalid-name

    def json_repr(self):
        return {
            'Action': self.Action,
            'Effect': self.Effect,
            'Resource': self.Resource,
        }

    def merge(self, other):
        """Merge two statements into one."""
        if self.Effect != other.Effect:
            raise ValueError("Trying to combine two statements with differing effects: {} {}".format(self.Effect,
                                                                                                     other.Effect))

        effect = self.Effect

        actions = list(sorted(set(self.Action + other.Action), key=lambda action: action.json_repr()))
        resources = list(sorted(set(self.Resource + other.Resource)))

        return Statement(
            Effect=effect,
            Action=actions,
            Resource=resources,
        )

    def __action_list_strings(self):
        return "-".join([a.json_repr() for a in self.Action])

    def __lt__(self, other):
        if self.Effect != other.Effect:
            return self.Effect < other.Effect
        if self.Action != other.Action:
            # pylint: disable=W0212
            return self.__action_list_strings() < other.__action_list_strings()

        return "".join(self.Resource) < "".join(other.Resource)


class PolicyDocument(BaseElement):
    """IAM Policy Doument."""

    def __init__(self, Statement, Version="2012-10-17"):  # pylint: disable=redefined-outer-name
        self.Version = Version  # pylint: disable=invalid-name
        self.Statement = Statement  # pylint: disable=invalid-name

    def json_repr(self):
        return {
            'Version': self.Version,
            'Statement': self.Statement
        }

    def to_json(self):
        """Render object into IAM Policy JSON"""
        return json.dumps(self.json_repr(), cls=IAMJSONEncoder, indent=4, sort_keys=True)


class IAMJSONEncoder(json.JSONEncoder):
    """JSON Encoder using the json_repr functions"""

    def default(self, o):  # pylint: disable=method-hidden
        if hasattr(o, 'json_repr'):
            return o.json_repr()
        return json.JSONEncoder.default(self, o)


def _parse_action(action):
    parts = action.split(":")
    return Action(parts[0], parts[1])


def _parse_statement(statement):
    return Statement(Action=[_parse_action(action) for action in statement['Action']],
                     Effect=statement['Effect'],
                     Resource=statement['Resource'])


def _parse_statements(json_data):
    # TODO: jsonData could also be dict, aka one statement; similar things happen in the rest of the policy pylint: disable=fixme
    # https://github.com/flosell/iam-policy-json-to-terraform/blob/fafc231/converter/decode.go#L12-L22
    return [_parse_statement(statement) for statement in json_data]


def parse_policy_document(stream):
    """Parse a stream of JSON data to a PolicyDocument object"""
    if isinstance(stream, six.string_types):
        json_dict = json.loads(stream)
    else:
        json_dict = json.load(stream)

    return PolicyDocument(_parse_statements(json_dict['Statement']), Version=json_dict['Version'])


def all_known_iam_permissions():
    "Return a list of all known IAM actions"
    with open(os.path.join(os.path.dirname(__file__), 'known-iam-actions.txt')) as iam_file:
        return {line.rstrip('\n') for line in iam_file.readlines()}


def known_iam_actions(prefix):
    """Return known IAM actions for a prefix, e.g. all ec2 actions"""
    # This could be memoized for performance improvements
    knowledge = pipe(all_known_iam_permissions(),
                     mapz(_parse_action),
                     groupbyz(lambda x: x.prefix))

    return knowledge.get(prefix, [])
