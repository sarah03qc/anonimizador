"""Source-distribution separation gate, without creating a Git repository."""
from pathlib import Path
import json,os,re,sys
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.venv','__pycache__','.pytest_cache','models','build','dist','release','reports','cache','.cache','.hf','huggingface','torch_extensions','.audit-cache','.pip-cache','downloads','.mypy_cache','.ruff_cache'}
def main():
    ignore=(ROOT/'.gitignore').read_text()
    required=['.venv/','__pycache__/','.pytest_cache/','models/','build/','dist/','release/','cache/','reports/']
    assert all(line in ignore.splitlines() for line in required)
    large=[];absolute=[];checked=0
    for folder,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in EXCLUDED and not (Path(folder).name=='test_data' and d=='gate2')]
        for name in files:
            path=Path(folder)/name
            if name.endswith(('.pyc','.pyo','.log','.tmp','.partial','.exe','.zip')):continue
            checked+=1
            if path.stat().st_size>100_000_000:large.append(str(path.relative_to(ROOT)))
            if path.suffix in ('.py','.ps1','.bat','.spec','.toml','.md','.txt'):
                content=path.read_text(encoding='utf-8-sig',errors='replace')
                if re.search(r'[A-Za-z]:[\\/]Users[\\/][^\s\\/]+[\\/]',content):absolute.append(str(path.relative_to(ROOT)))
    baseline=ROOT/'build/windows/resources/functional_baseline.json'
    import hashlib
    unchanged=all(hashlib.file_digest((ROOT/p).open('rb'),'sha256').hexdigest()==sha for p,sha in json.loads(baseline.read_text()).items())
    report={'result':'PASS' if not large and not absolute and unchanged else 'FAIL','source_files_checked':checked,'large_source_files':large,'machine_absolute_paths_in_source':absolute,'functional_application_and_prior_tests_unchanged':unchanged,'git_repository_created':False,'commit':False,'push':False,'excluded_artifacts':sorted(EXCLUDED)}
    (ROOT/'reports/windows_source_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    assert report['result']=='PASS'
if __name__=='__main__':main()
