#!/bin/bash
set -e

SCRIPT_DIR=$(cd $(dirname $0) ; pwd -P)
VENV_DIR="${SCRIPT_DIR}/trailscraper-venv"

activate_venv() {
    source "${VENV_DIR}/bin/activate"
}

create_venv() {
    if which python3 > /dev/null; then
        PYTHON_BINARY_NAME="python3"
    else
        PYTHON_BINARY_NAME="python"
    fi

    ${PYTHON_BINARY_NAME} --version 2>&1 | grep -q 'Python 3'  || die "python is not Python 3"

    virtualenv -p ${PYTHON_BINARY_NAME} "${VENV_DIR}"
}

goal_test() {
    activate_venv
    python setup.py test
}

goal_check() {
    activate_venv
    pylint trailscraper
}

goal_trailscraper() {
    activate_venv
    trailscraper-venv/bin/trailscraper $@
}

goal_setup() {
    if [ ! -d "${VENV_DIR}" ]; then
        create_venv
    fi

    activate_venv

    pushd "${SCRIPT_DIR}" > /dev/null
      pip3 install -r requirements-dev.txt
      python setup.py develop
    popd > /dev/null
}

goal_generate-rst() {
    pushd "${SCRIPT_DIR}" > /dev/null
    for f in "README.md" "CHANGELOG.md"; do
        output_file="$(basename ${f} .md).rst"
        pandoc --from=markdown --to=rst --output="${output_file}" "${f}"
    done
    popd > /dev/null
}

goal_clean() {
	rm -rf "${VENV_DIR}"

    pushd "${SCRIPT_DIR}" > /dev/null
    rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

    popd > /dev/null
}

if type -t "goal_$1" &>/dev/null; then
  goal_$1 ${@:2}
else
  echo "usage: $0 <goal>
goal:
    setup        -- set up development environment
    test         -- run all tests
    check        -- run all style checks"
  exit 1
fi
