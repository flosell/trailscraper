#!/bin/bash
set -e

SCRIPT_DIR=$(cd $(dirname $0) ; pwd -P)
VENV_DIR="${SCRIPT_DIR}/venvs/trailscraper-venv${VENV_POSTFIX}"
VERSIONS="3.10
3.11
3.12
3.13"

activate_venv() {
    source "${VENV_DIR}/bin/activate"
}

goal_regenerate_iam_data_from_cloudonaut() {
    tmp_dir=$(mktemp -d)
    pushd ${tmp_dir} > /dev/null
        git clone --depth 1 git@github.com:widdix/complete-aws-iam-reference.git
        cd complete-aws-iam-reference/tools
        node md2json.js | \
            tee ${SCRIPT_DIR}/tests/iam-actions-from-cloudonaut.json | \
            jq -r '.[] | .service+":"+.action' | \
            sort | \
            uniq > ${SCRIPT_DIR}/tests/iam-actions-from-cloudonaut.txt
    popd > /dev/null
}

goal_regenerate_iam_data_from_policy_sim() {
    curl https://raw.githubusercontent.com/rvedotrc/aws-iam-reference/master/all-actions.txt |\
        sort | \
        uniq > ${SCRIPT_DIR}/tests/iam-actions-from-policy-sim.txt
}

goal_merge_iam_data() {
    cat ${SCRIPT_DIR}/tests/iam-actions-from-cloudonaut.txt \
        ${SCRIPT_DIR}/tests/iam-actions-from-policy-sim.txt | \
      sort | uniq >   ${SCRIPT_DIR}/tests/known-iam-actions.txt
}

goal_regenerate_iam_data() {
    goal_regenerate_iam_data_from_cloudonaut
    goal_regenerate_iam_data_from_policy_sim
    goal_merge_iam_data
}
goal_unknown-actions() {
    activate_venv

    python3 "${SCRIPT_DIR}/tests/list_unknown_actions.py" > unknown_actions.txt
}

goal_in-version() {
    python_version=$1
    cmd="/code/go ${@:2}"
    echo "=============== BEGIN Python ${python_version} ${cmd} ==============="

    docker run -i \
               -v $(pwd):/code \
               -w /code \
               -e VENV_POSTFIX=${python_version} \
               ghcr.io/astral-sh/uv:python${python_version}-trixie-slim ${cmd}

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
    venv_dir="$1"
    python3 --version
    which python3

    uv venv "${venv_dir}"
}

goal_test() {
    # make build not fail on travisci when working with boto and moto... https://github.com/spulec/moto/issues/1771
    export BOTO_CONFIG=/dev/null
    export AWS_SECRET_ACCESS_KEY=foobar_secret
    export AWS_ACCESS_KEY_ID=foobar_key

    pushd "${SCRIPT_DIR}" > /dev/null
      activate_venv
      pytest
    popd > /dev/null
}

goal_test-setuptools() {
    goal_clean
    local last_python_version=$(echo "${VERSIONS}" | sort | tail -n 1)
    local python_version="${TRAVIS_PYTHON_VERSION:-${last_python_version}}"

    echo "Running Python ${python_version} in clean docker container..."

    pushd "${SCRIPT_DIR}" > /dev/null
        docker run -i -v $(pwd):/app python:${python_version} bash <<-EOF
cd /app
pip install uv
uv pip install --system .

echo '{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "s3:GetObject"
         ],
         "Resource":"arn:aws:s3:::my_corporate_bucket/home/${aws:userid}/*"
      }
   ]
}' | trailscraper guess

cat tests/integration/events-for-smoke-test.json | trailscraper generate
EOF
    popd > /dev/null
}

goal_test-docker-build() {
    goal_clean
    cd ${SCRIPT_DIR}
    docker build -t trailscraper-docker-test .
    docker run --rm trailscraper-docker-test --version
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
        create_venv "${VENV_DIR}"
    fi

    pushd "${SCRIPT_DIR}" > /dev/null
      activate_venv
      uv pip install -e ".[dev]"
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

goal_bump-homebrew-release() {
  export HOMEBREW_GITHUB_API_TOKEN="$(gh auth token)" # homebrew often uses a readonly token, set the one already used for release instead
  local version="$1"
  brew bump-formula-pr --verbose \
                       --version "${version}" \
                       trailscraper
}

goal_create_github_container_registry_release() {
  local version="$1"
  echo $GITHUB_TOKEN | docker login ghcr.io -u flosell --password-stdin

  pushd "${SCRIPT_DIR}" > /dev/null

  docker build -t ghcr.io/flosell/trailscraper:latest \
               -t ghcr.io/flosell/trailscraper:${version} \
               .

  docker push ghcr.io/flosell/trailscraper:latest
  docker push ghcr.io/flosell/trailscraper:${version}

  popd > /dev/null
}

goal_release() {
    echo "Checking GitHub Login..."
    gh auth status | grep -E 'Token scopes.*workflow'
    if [ $? -ne 0 ]; then
      echo "Please login to GitHub using 'gh auth login' and afterwards, ensure the token has the 'workflow' scope using 'gh auth refresh -s workflow'"
      exit 1
    fi
    gh auth status | grep -E 'Token scopes.*write:packages'
    if [ $? -ne 0 ]; then
      echo "Please login to GitHub using 'gh auth login' and afterwards, ensure the token has the 'workflow' scope using 'gh auth refresh -s workflow'"
      exit 1
    fi

    export GITHUB_TOKEN=$(gh auth token)

    VERSION=$(chag latest)

    echo "Version to release is ${VERSION}."
    echo
    echo "A few things to check:"
    echo "* Is this really the version you want to release? Have there been major changes that require a different version?"
    echo "* Are you sure that CHANGELOG.md, pyproject.toml and __init__.py all show this version?"
    echo
    (cd ${SCRIPT_DIR} && grep ${VERSION} pyproject.toml \
                                      CHANGELOG.md \
                                      trailscraper/__init__.py | sed 's/^/  /')
    echo
    echo "Hit ENTER if you are ok and want to continue"
    read

    goal_test
    goal_check

    goal_generate-rst

    uv build
    twine upload --sign --identity 'florian.sellmayr@gmail.com' dist/*

    goal_tag_version
    goal_create_github_release
    goal_create_github_container_registry_release ${VERSION}

    goal_bump_version
    git push

    goal_bump-homebrew-release ${VERSION}
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
    setup               -- set up development environment
    test                -- run all functional tests
    test-setuptools     -- run a smoke-test after installing in a clean environment
    test-docker-build   -- run a smoke-test after building a clean docker container
    check               -- run all style checks

    trailscraper        -- call the current development state

    in-version          -- run a go-command in a particular version of python
    in-all-versions     -- run a go-command in all supported versions of python

    release             -- create and publish a new release
    bump_version        -- bump version

    regenerate_iam_data -- regenerate list of known iam actions
    unknown-actions     -- regenerate list of unknown actions
    "
  exit 1
fi
