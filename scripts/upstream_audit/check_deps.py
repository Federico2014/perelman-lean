import json
import subprocess
from pathlib import Path
root=Path('/work/proof')
manifest=json.loads((root/'lake-manifest.json').read_text())
for package in manifest['packages']:
    path=root/'.lake/packages'/package['name']
    actual=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
    if actual!=package['rev']:
        raise SystemExit(f"Dependency mismatch: {package['name']} {actual}")
    print(package['name'],actual,flush=True)
print('All actual dependency commits match the fixed manifest',flush=True)
