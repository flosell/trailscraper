#!/usr/bin/env python
from tests.test_utils_iam import all_aws_api_methods, all_known_iam_permissions
from trailscraper.cloudtrail import Record

if __name__ == "__main__":
    iam_permissions_from_api_calls = set()
    for api_call in all_aws_api_methods():
        x = api_call.split(":")
        r = Record(x[0], x[1])
        iam_permissions_from_api_calls.add(r.to_statement().Action[0].json_repr())

    known_permissions = all_known_iam_permissions()
    unknown_permissions = iam_permissions_from_api_calls.difference(known_permissions)

    for action in sorted(unknown_permissions):
        print action
