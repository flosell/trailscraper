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
])
def test_create_base_action(test_input, expected):
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
        # Is this the best result? Aren't we usually just interested in Attach-Detach?
        Action('ec2', 'CreateVolume'),
        Action('ec2', 'DeleteVolume'),
        Action('ec2', 'AttachVolume'),
        Action('ec2', 'DescribeVolumes'),
    ]),
    (Action('ecr', 'ListImages'), [
        # Is this the best result? Aren't we usually just interested in Attach-Detach?
        Action('ecr', 'DescribeImages'),

    ]),
])
def test_find_create_action(test_input, expected):
    assert test_input.matching_actions() == expected


    # TODO:
    # * Encrypt/Decrypt/GenerateDataKey?
    # * Put
    # * ecr:BatchDeleteImage, ecr:BatchGetImage
    # * deregister
    # * modify
    # * remove