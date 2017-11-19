from trailscraper.policy_generator import _source_to_iam_prefix


def test_should_map_normal_event_sources_to_iam_prefix():
    assert _source_to_iam_prefix('autoscaling.amazonaws.com') == 'autoscaling'
    assert _source_to_iam_prefix('sts.amazonaws.com') == 'sts'
    assert _source_to_iam_prefix('ec2.amazonaws.com') == 'ec2'


def test_should_map_special_cases():
    assert _source_to_iam_prefix('monitoring.amazonaws.com') == 'cloudwatch'


def test_should_map_unknown_sources():
    assert _source_to_iam_prefix('unknown.amazonaws.com') == 'unknown'
