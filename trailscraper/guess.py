"""Logic to guess related IAM statements"""
from trailscraper.iam import PolicyDocument, Statement


def _guess_actions(actions):
    return [item for action in actions
            for item in action.matching_actions()]


def _extend_statement(statement):
    extended_actions = _guess_actions(statement.Action)
    if extended_actions:
        return [statement, Statement(Action=extended_actions,
                                     Effect=statement.Effect,
                                     Resource=["*"])]

    return [statement]


def guess_statements(policy):
    """Guess additional create actions"""
    extended_statements = [item for statement in policy.Statement
                           for item in _extend_statement(statement)]

    return PolicyDocument(Version=policy.Version, Statement=extended_statements)
