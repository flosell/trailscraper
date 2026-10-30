import pytest

from trailscraper.iam import Action


@pytest.mark.parametrize("test_input,expected", [
    (Action('autoscaling', 'DescribeLaunchConfigurations'), "LaunchConfiguration"),
    (Action('autoscaling', 'CreateLaunchConfiguration'), "LaunchConfiguration"),
    (Action('autoscaling', 'DeleteLaunchConfiguration'), "LaunchConfiguration"),
    (Action('autoscaling', 'UpdateAutoScalingGroup'), "AutoScalingGroup"),
    (Action('ec2', 'DetachVolume'), "Volume"),
    (Action('ec2', 'AttachVolume'), "Volume"),
    (Action('ecr', 'ListImages'), "Image"),
    (Action('s3', 'PutObject'), "Object"),
    (Action('s3', 'GetObject'), "Object"),
    (Action('kms', 'Encrypt'), ""),
    (Action('kms', 'GenerateDataKey'), ""),
    (Action('ecr', 'BatchDeleteImage'), "Image"),
    (Action('ec2', 'DeregisterImage'), "Image"),
    (Action('dms', 'ModifyEndpoint'), "Endpoint"),
    (Action('elasticloadbalancing', 'RemoveTags'), "Tag"),
    (Action('apigateway', 'GET'), ""),
])
def test_base_action(test_input, expected):
    assert test_input._base_action() == expected


@pytest.mark.parametrize("test_input,expected", [
    (Action('autoscaling', 'DescribeLaunchConfigurations'), [
        Action('autoscaling', 'CreateLaunchConfiguration'),
        Action('autoscaling', 'DeleteLaunchConfiguration'),
    ]),
    (Action('autoscaling', 'CreateLaunchConfiguration'), [
        Action('autoscaling', 'DeleteLaunchConfiguration'),
        Action('autoscaling', 'DescribeLaunchConfigurations'),
    ]),
    (Action('autoscaling', 'DeleteLaunchConfiguration'), [
        Action('autoscaling', 'CreateLaunchConfiguration'),
        Action('autoscaling', 'DescribeLaunchConfigurations'),
    ]),
    (Action('autoscaling', 'UpdateAutoScalingGroup'), [
        Action('autoscaling', 'CreateAutoScalingGroup'),
        Action('autoscaling', 'DeleteAutoScalingGroup'),
        Action('autoscaling', 'DescribeAutoScalingGroups'),
    ]),
    (Action('autoscaling', 'DeleteAutoScalingGroup'), [
        Action('autoscaling', 'CreateAutoScalingGroup'),
        Action('autoscaling', 'UpdateAutoScalingGroup'),
        Action('autoscaling', 'DescribeAutoScalingGroups'),
    ]),
    (Action('ec2', 'DetachVolume'), [
        Action('ec2', 'CreateVolume'),
        Action('ec2', 'DeleteVolume'),
        Action('ec2', 'AttachVolume'),
        Action('ec2', 'ModifyVolume'),
        Action('ec2', 'DescribeVolumes'),
    ]),
    (Action('ecr', 'ListImages'), [
        Action('ecr', 'PutImage'),
        Action('ecr', 'DescribeImages'),
    ]),
    (Action('s3', 'PutObject'), [
        Action('s3', 'DeleteObject'),
        Action('s3', 'GetObject'),
        Action('s3', 'ListObjects'),
    ]),
    (Action('kms', 'Encrypt'), [
        Action('kms', 'GenerateDataKey'),
        Action('kms', 'Decrypt'),
    ]),
    (Action('ecr', 'BatchDeleteImage'), [
        Action('ecr', 'PutImage'),
        Action('ecr', 'DescribeImages'),
        Action('ecr', 'ListImages'),
    ]),
    (Action('ec2', 'DeregisterImage'), [
        Action('ec2', 'CreateImage'),
        Action('ec2', 'RegisterImage'),
        Action('ec2', 'DescribeImages'),
    ]),
    (Action('dms', 'ModifyEndpoint'), [
        Action('dms', 'CreateEndpoint'),
        Action('dms', 'DeleteEndpoint'),
        Action('dms', 'DescribeEndpoints'),
    ]),
    (Action('elasticloadbalancing', 'RemoveTags'), [
        Action('elasticloadbalancing', 'DescribeTags'),
        Action('elasticloadbalancing', 'AddTags'),
    ]),
    (Action('apigateway', 'GET'), [
        Action('apigateway', 'DELETE'),
        Action('apigateway', 'HEAD'),
        Action('apigateway', 'OPTIONS'),
        Action('apigateway', 'PATCH'),
        Action('apigateway', 'POST'),
        Action('apigateway', 'PUT'),
    ]),
])
def test_find_matching_actions_without_filtering(test_input, expected):
    assert test_input.matching_actions(allowed_prefixes=None) == expected


@pytest.mark.parametrize("test_input,expected,allowed_prefixes", [
    (Action('ec2', 'DetachVolume'), [
        Action('ec2', 'AttachVolume'),
    ], ['Attach']),
])
def test_find_matching_actions_with_filtering(test_input, expected, allowed_prefixes):
    assert test_input.matching_actions(allowed_prefixes=allowed_prefixes) == expected
