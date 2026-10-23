#!/bin/sh
set -eu
ln -s /work/proof /work/proof/.lake/packages/poincareConjecture
ln -s /work/proof/.lake/packages .lake/packages
lake --no-cache build
printf 'FullAudit source check begins\n'
lake env lean -DwarningAsError=true FullAudit.lean
lake env leanchecker -v PerelmanFull
