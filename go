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
    pytest -v
}

goal_trailscraper() {
    activate_venv
    bin/trailscraper $@
}


goal_setup() {
    if [ ! -d "${VENV_DIR}" ]; then
        create_venv
    fi

    activate_venv

    pip3 install -r requirements.txt
    pip3 install -r requirements-test.txt
}


if type -t "goal_$1" &>/dev/null; then
  goal_$1 ${@:2}
else
  echo "usage: $0 <goal>
goal:
    setup        -- set up development environment
    test         -- run all tests"
  exit 1
fi
