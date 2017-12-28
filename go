#!/bin/bash
set -e

SCRIPT_DIR=$(cd $(dirname $0) ; pwd -P)
VENV_DIR="${SCRIPT_DIR}/venvs/trailscraper-venv${VENV_POSTFIX}"
VERSIONS="2.7
3.4
3.5
3.6"

activate_venv() {
    source "${VENV_DIR}/bin/activate"
    python --version
    pip --version
    which python
}

goal_in-version() {
    python_version=$1
    cmd="/code/go ${@:2}"
    echo "=============== BEGIN Python ${python_version} ${cmd} ==============="

    docker run -i \
               -v $(pwd):/code \
               -w /code \
               -e VENV_POSTFIX=${python_version} \
               python:${python_version} ${cmd}

    echo "=============== END Python ${python_version} ${cmd}   ==============="
}

goal_in-all-versions() {
    if [ "${parallel}" == "parallel" ]; then
        parallel --tag "./go in-version {} ${@}" ::: "$VERSIONS"
    else
        for version in ${VERSIONS}; do
            goal_in-version ${version} ${@}
        done
    fi
}

create_venv() {
    python --version
    pip --version
    which python

    PYTHON_BINARY_NAME="python"

    if which virtualenv > /dev/null; then
        virtualenv -p ${PYTHON_BINARY_NAME} "${VENV_DIR}"
    else
        pyvenv "${VENV_DIR}"
    fi

}

goal_test() {
    pushd "${SCRIPT_DIR}" > /dev/null
      activate_venv
      python setup.py test
    popd > /dev/null
}

goal_check() {
    pushd "${SCRIPT_DIR}" > /dev/null
      activate_venv
      pylint trailscraper
    popd > /dev/null
}

goal_trailscraper() {
    activate_venv
    ${VENV_DIR}/bin/trailscraper "$@"
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

    pushd "${SCRIPT_DIR}" > /dev/null
      activate_venv
      pip install -r requirements-dev.txt
      python setup.py develop
    popd > /dev/null
}


goal_clean() {
	rm -rf "${VENV_DIR}"

    pushd "${SCRIPT_DIR}" > /dev/null
    set +e # It's OK if some of the things we want to delete aren't there

    rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -f README.rst
	rm -f CHANGELOG.rst
	find . -name '*.egg-info' -exec rm -vfr {} +
	find . -name '*.egg' -exec rm -vf {} +

	find . -name '*.pyc' -exec rm -vf {} +
	find . -name '*.pyo' -exec rm -vf {} +
	find . -name '*~' -exec rm -vf {} +
	find . -name '__pycache__' -exec rm -vfr {} +

    set -e
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
    goal_test
    goal_check

    goal_generate-rst

    python setup.py sdist bdist_wheel upload --sign --identity 'florian.sellmayr@gmail.com' -r 'https://www.python.org/pypi'

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
  goal_$1 "${@:2}"
else
  echo "usage: $0 <goal>
goal:
    setup              -- set up development environment
    test               -- run all tests
    check              -- run all style checks

    trailscraper       -- call the current development state

    in-version         -- run a go-command in a particular version of python
    in-all-versions    -- run a go-command in all supported versions of python

    release            -- create and publish a new release
    bump_version       -- bump version"
  exit 1
fi
