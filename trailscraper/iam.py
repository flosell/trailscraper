"""Classes to deal with IAM Policies"""
import json


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
        elif self.Action != other.Action:
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
