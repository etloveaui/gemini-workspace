#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "Venv ready at ./venv"

