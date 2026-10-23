import json,re,subprocess
from pathlib import Path
root=Path('/work/proof')
packages=json.loads((root/'lake-manifest.json').read_text())['packages']
for package in packages:
    name,url,rev=package['name'],package['url'],package['rev']
    if not re.fullmatch(r'[A-Za-z0-9_-]+',name) or not re.fullmatch(r'[0-9a-f]{40}',rev):
        raise SystemExit('Invalid package name or revision')
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',url):
        raise SystemExit('Unexpected package source')
    path=root/'.lake/packages'/name
    if path.is_dir():
        result=subprocess.run(['git','-C',str(path),'rev-parse','HEAD'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if result.returncode==0 and result.stdout.strip()==rev:
            print('Reusing pinned dependency',name,rev,flush=True)
            continue
        raise SystemExit(f'Existing dependency has unexpected state: {name}')
    path.mkdir(parents=True)
    print('Fetching pinned dependency',name,rev,flush=True)
    subprocess.run(['git','-C',str(path),'init','-q'],check=True)
    subprocess.run(['git','-C',str(path),'remote','add','origin',url],check=True)
    subprocess.run(['git','-C',str(path),'fetch','--depth=1','origin',rev],check=True)
    subprocess.run(['git','-C',str(path),'-c','advice.detachedHead=false','checkout','--detach',rev],check=True)
