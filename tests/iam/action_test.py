import pytest

from trailscraper.iam import Action


@pytest.mark.parametrize("test_input,expected", [
    (Action('autoscaling', 'DescribeLaunchConfigurations'), "LaunchConfiguration"),
    (Action('autoscaling', 'CreateLaunchConfiguration'), "LaunchConfiguration"),
    (Action('autoscaling', 'DeleteLaunchConfiguration'), "LaunchConfiguration"),
    (Action('autoscaling', 'UpdateAutoScalingGroup'), "AutoScalingGroup"),
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
])
def test_find_create_action(test_input, expected):
    assert test_input.matching_actions() == expected


# TODO:
# * Attach/Detach?
# * list
# * Encrypt/Decrypt/GenerateDataKey?
# * Put