#!/usr/bin/env bash

PROJECT=paralarva
BASEDIR=$(dirname "$0")
[[ -z ${BASEDIR} ]] && BASEDIR='.'
VENV=${BASEDIR}/${PROJECT}-venv
if [[ ! -f "${VENV}/bin/python3" ]]; then
  rm -Rf ${VENV}
  virtualenv -p python3 "${VENV}" --always-copy
fi
source ${VENV}/bin/activate
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -r requirements.txt
"${VENV}/bin/python" -m pip install -r tests-requirements.txt
"${VENV}/bin/python" -m pip install -r extra-requirements.txt
python3 "${BASEDIR}/setup.py" develop
