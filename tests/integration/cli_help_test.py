from click.testing import CliRunner

from trailscraper import cli


def test_should_output_help_message_by_default():
    runner = CliRunner()
    result = runner.invoke(cli.root_group)
    assert result.exit_code == 0
    assert 'Usage:' in result.output
