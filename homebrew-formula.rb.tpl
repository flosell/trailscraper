class Trailscraper < Formula
  include Language::Python::Virtualenv

  desc "Tool to get valuable information out of AWS CloudTrail"
  homepage "https://github.com/flosell/trailscraper"
  url "${release_url}"
  sha256 "${release_sha}"
  license "Apache-2.0"

${old_bottles}

  depends_on "python@3.8"

${resources}

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/trailscraper --version")

    test_input = '{"Records": []}'
    output = shell_output("echo '#{test_input}' | trailscraper generate")
    assert_match "Statement", output
  end
end
