#!/bin/bash
set -e

SCRIPT_DIR=$(cd $(dirname $0) ; pwd -P)
VENV_DIR="${SCRIPT_DIR}/trailscraper-venv"

activate_venv() {
    source "${VENV_DIR}/bin/activate"
}

create_venv() {
    virtualenv "${VENV_DIR}"
}

goal_test() {
    activate_venv
    python setup.py test
}

goal_test-all-versions() {
    activate_venv
    tox
}

goal_check() {
    activate_venv
    pylint trailscraper
}

goal_trailscraper() {
    activate_venv
    trailscraper-venv/bin/trailscraper $@
}

goal_generate-rst() {
    pushd "${SCRIPT_DIR}" > /dev/null
    for f in "README.md" "CHANGELOG.md"; do
        output_file="$(basename ${f} .md).rst"
        pandoc --from=markdown --to=rst --output="${output_file}" "${f}"
    done
    popd > /dev/null
}

goal_setup() {
    if [ ! -d "${VENV_DIR}" ]; then
        create_venv
    fi

    activate_venv
    goal_generate-rst

    pushd "${SCRIPT_DIR}" > /dev/null
      pip install -r requirements-dev.txt
      python setup.py develop
    popd > /dev/null
}


goal_clean() {
	rm -rf "${VENV_DIR}"

    pushd "${SCRIPT_DIR}" > /dev/null
    rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .tox/
	rm -f README.rst
	rm -f CHANGELOG.rst
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

    popd > /dev/null
}

goal_create_github_release() {
    # make sure you have the following:
    # https://github.com/aktau/github-release
    # https://github.com/mtdowling/chag
    # $GITHUB_TOKEN is set

    pushd "${SCRIPT_DIR}" > /dev/null
    VERSION=$(chag latest)
    CHANGELOG=$(chag contents)
    USER="flosell"
    REPO="trailscraper"

    echo "Publishing Release to GitHub: "
    echo "Version ${VERSION}"
    echo "${CHANGELOG}"
    echo

    github-release release \
        --user ${USER} \
        --repo ${REPO} \
        --tag ${VERSION} \
        --name ${VERSION} \
        --description "${CHANGELOG}"

    echo "Published release on GitHub"
    popd > /dev/null
}

goal_tag_version() {
    VERSION=$(chag latest)
    git tag -s ${VERSION} -m "Release ${VERSION}"
    git push --tags
}

goal_bump_version() {
    part=${1:-patch}
    activate_venv
    bumpversion ${part}
}

goal_release() {
    goal_test-all-versions
    goal_check

    goal_generate-rst

    python setup.py sdist bdist_wheel upload --sign --identity 'florian.sellmayr@gmail.com'

    goal_tag_version
    goal_create_github_release
    goal_bump_version
    git push
}

goal_push() {
    goal_test
    goal_check
    git push
}

if type -t "goal_$1" &>/dev/null; then
  goal_$1 ${@:2}
else
  echo "usage: $0 <goal>
goal:
    setup              -- set up development environment
    test               -- run all tests
    test-all-versions  -- run all tests
    check              -- run all style checks

    trailscraper       -- call the current development state

    release            -- create and publish a new release
    bump_version       -- bump version"
  exit 1
fi
