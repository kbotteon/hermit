#!/usr/bin/env bash
################################################################################
# \brief Environment setup scripts
#
# (C) 2024 Kyle Botteon
# This file is part of HERMIT. Refer to the LICENSE in that repository.
################################################################################

VENV_DIR="./.venv"
START_DIR=$(pwd)
SCRIPT_PATH="${BASH_SOURCE[0]}"

################################################################################
# Check Preconditions
################################################################################

# Always execute out of script directory
cd $(dirname "$(readlink -f "${SCRIPT_PATH}")"})

# Script must be sourced to work
if [[ "${SCRIPT_PATH}" == "${0}" ]]; then
    echo "ERROR: This script should be sourced, not executed"
    return 1
fi

# Ensure python3 is installed
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is not installed"
    return 1
fi

# Ensure python3-venv is installed
if ! python3 -c "import venv" &>/dev/null; then
    echo "ERROR: python3-venv is not installed"
    return 1
fi

################################################################################
# Process Arguments
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--clean)
            deactivate
            rm -rf "${VENV_DIR}"
            shift
            ;;
        *)
            echo "Invalid option ${1}" >&2
            return 1
            ;;
    esac
done

################################################################################
# Run Script
################################################################################


if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
    source "${VENV_DIR}/bin/activate"
    pip install --upgrade pip
    pip install setuptools wheel
    pip install -r ./tools/requirements.txt
else
    source "${VENV_DIR}/bin/activate"
fi
