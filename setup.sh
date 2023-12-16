#!/usr/bin/env bash

VENV_DIR="./.venv"
START_DIR=$(pwd)

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    printf "This script should be sourced, not executed\n"
    exit 1
fi

cd $(dirname "$(readlink -f "${BASH_SOURCE[0]}")"})

# TODO: Ensure python3 is installed
# TODO: Ensure python3-venv is installed

if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv ${VENV_DIR}
    source ${VENV_DIR}/bin/activate
    pip install --upgrade pip
    pip install setuptools wheel
    pip install -r ./script/requirements.txt
else
    source ${VENV_DIR}/bin/activate
fi
