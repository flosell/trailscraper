#!/usr/bin/env python
from tests.cloudtrail.map_to_iam_sanity_test import unknown_actions

if __name__ == "__main__":
    for action in sorted(unknown_actions()):
        print action
