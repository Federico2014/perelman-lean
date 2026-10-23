#!/bin/sh
set -eu
lake --no-cache build +PoincareConjecture.Proofs.Main
lake env lean PoincareConjecture/Proofs/Main.lean
lake env lean --root=/audit -DwarningAsError=true -o .lake/build/lib/lean/AuditTarget.olean /audit/AuditTarget.lean
lake env lean --root=/audit -DwarningAsError=true -o .lake/build/lib/lean/AuditBridge.olean /audit/AuditBridge.lean
