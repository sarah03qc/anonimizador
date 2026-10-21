"""Static release gate: exact assets, GUI executable, local model and clean payload."""
from pathlib import Path
import hashlib,json,sys,re
import pefile

ROOT=Path(__file__).resolve().parents[1]
def validate(folder):
    folder=Path(folder).resolve();internal=folder/'_internal'
    exe=folder/'Anonimizador CEN-CINAI.exe'
    assert pefile.PE(str(exe),fast_load=True).OPTIONAL_HEADER.Subsystem==2,'Executable must use Windows GUI subsystem'
    for relative in ['app.py','.streamlit/config.toml','profiles/synthetic_demo_profile.yaml','python312.dll','assets/anonimizador.ico']:
        assert (internal/relative).is_file(),f'Missing resource: {relative}'
    manifest=json.loads((ROOT/'model_manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        path=internal/'models/spanish-pii'/name
        assert path.is_file() and hashlib.file_digest(path.open('rb'),'sha256').hexdigest()==expected,f'Model integrity: {name}'
    forbidden={'.git','.venv','reports','tests','test_data','testdata','candidates','.pytest_cache','build','release'}
    files=list(folder.rglob('*'))
    assert not any(forbidden.intersection(p.relative_to(folder).parts) for p in files),'Development assets leaked'
    assert not list(folder.rglob('*.partial'))
    for path in [internal/'app.py',*(internal/'anonymizer').glob('*.py')]:
        if path.is_file():assert not re.search(r'[A-Za-z]:[\\/]Users[\\/]',path.read_text(encoding='utf-8-sig'))
    assert (folder/'LEAME.txt').is_file() and (folder/'LICENSES/inventory.json').is_file()
    return {'static_bundle':'PASS','root':str(folder),'gui_subsystem':True,'model_sha256':'PASS','project_tests_datasets_qa_excluded':True,'bytes':sum(p.stat().st_size for p in files if p.is_file()),'files':sum(p.is_file() for p in files)}
if __name__=='__main__':print(json.dumps(validate(sys.argv[1]),indent=2))
