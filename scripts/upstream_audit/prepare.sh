#!/bin/sh
set -eu
id
lean --version
lake --version
python3 /audit/fetch_pinned.py
lake exe cache get
python3 /audit/check_deps.py
git diff --exit-code -- lakefile.toml lake-manifest.json lean-toolchain PoincareConjecture PoincareLib
