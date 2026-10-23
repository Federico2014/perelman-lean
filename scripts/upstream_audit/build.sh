#!/bin/sh
set -eu
printf 'Build start: '
date -u '+%Y-%m-%dT%H:%M:%SZ'
lean --version
lake --version
printf 'Pinned source: '
git rev-parse HEAD
python3 /audit/check_deps.py
python3 - <<'PY'
from pathlib import Path
import os
root=Path('/work/proof/.lake/build/lib/lean')
files=list((root/'PoincareLib').rglob('*.olean'))+list((root/'PoincareConjecture').rglob('*.olean'))
if os.environ.get('PERELMAN_RESUME_BUILD') == '1':
    print(f'Resuming our own pinned source build: {len(files)} candidate modules cached',flush=True)
elif files:
    raise SystemExit(f'Fresh-build precondition failed: {len(files)} candidate oleans already exist')
else:
    print('Fresh-build precondition: no precompiled candidate modules',flush=True)
PY
lake --no-cache build
printf 'Build end: '
date -u '+%Y-%m-%dT%H:%M:%SZ'
git diff --exit-code -- lakefile.toml lake-manifest.json lean-toolchain PoincareConjecture PoincareLib
