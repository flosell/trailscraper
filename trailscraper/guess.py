"""Logic to guess related IAM statements"""
from trailscraper.iam import PolicyDocument, Statement


def _guess_actions(actions, allowed_prefixes):
    return [item for action in actions
            for item in action.matching_actions(allowed_prefixes)]


def _extend_statement(statement, allowed_prefixes):
    extended_actions = _guess_actions(statement.Action, allowed_prefixes)
    if extended_actions:
        return [statement, Statement(Action=extended_actions,
                                     Effect=statement.Effect,
                                     Resource=["*"])]

    return [statement]


def guess_statements(policy, allowed_prefixes):
    """Guess additional create actions"""
    extended_statements = [item for statement in policy.Statement
                           for item in _extend_statement(statement, allowed_prefixes)]

    return PolicyDocument(Version=policy.Version, Statement=extended_statements)
