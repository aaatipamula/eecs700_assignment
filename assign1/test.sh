#!/bin/bash

set -e

PYTHON_BIN="uv run"

for f in tests/*.py; do
  echo "=== Testing on $f ==="
  $PYTHON_BIN prover.py $f
  echo
done
