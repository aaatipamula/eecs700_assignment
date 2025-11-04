#!/bin/bash

set -e

for f in tests/*.py; do
  echo "=== Testing on $f ==="
  uv run prover.py $f
  echo
done
