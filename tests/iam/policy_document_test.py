
from trailscraper.iam import PolicyDocument, Statement, Action


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
    assert pd.to_json() == expected_json