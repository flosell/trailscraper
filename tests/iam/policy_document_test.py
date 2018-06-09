import json
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


from trailscraper.iam import PolicyDocument, Statement, Action, parse_policy_document


def test_policy_document_renders_to_json():
    pd = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'DescribeLaunchConfigurations'),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action('sts', 'AssumeRole'),
                ],
                Resource=[
                    "arn:aws:iam::111111111111:role/someRole"
                ]
            )
        ]
    )

    expected_json = '''\
{
    "Statement": [
        {
            "Action": [
                "autoscaling:DescribeLaunchConfigurations"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        },
        {
            "Action": [
                "sts:AssumeRole"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:iam::111111111111:role/someRole"
            ]
        }
    ],
    "Version": "2012-10-17"
}'''
    assert json.loads(pd.to_json()) == json.loads(expected_json)


def test_json_parses_to_policy_document():
    pd = PolicyDocument(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect="Allow",
                Action=[
                    Action('autoscaling', 'DescribeLaunchConfigurations'),
                ],
                Resource=["*"]
            ),
            Statement(
                Effect="Allow",
                Action=[
                    Action('sts', 'AssumeRole'),
                ],
                Resource=[
                    "arn:aws:iam::111111111111:role/someRole"
                ]
            )
        ]
    )

    assert parse_policy_document(StringIO(pd.to_json())).to_json() == pd.to_json()

