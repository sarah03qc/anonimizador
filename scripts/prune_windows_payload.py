"""Remove upstream test fixtures collected as data, never runtime library APIs."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
    bundle=(ROOT/'dist/Anonimizador_CEN-CINAI').resolve()
    internal=(bundle/'_internal').resolve()
    assert bundle.is_relative_to(ROOT.resolve()) and internal.is_relative_to(bundle)
    markers={'tests','test_data','testdata'};removed=[];size=0
    files=[p for p in internal.rglob('*') if p.is_file() and markers.intersection(p.relative_to(internal).parts)]
    # Resolve every target first, before any deletion. No following external links.
    assert all(p.resolve().is_relative_to(internal) for p in files)
    for path in files:
        size+=path.stat().st_size;removed.append(path.relative_to(bundle).as_posix());path.unlink()
    folders=[p for p in internal.rglob('*') if p.is_dir() and markers.intersection(p.relative_to(internal).parts)]
    assert all(p.resolve().is_relative_to(internal) for p in folders)
    for path in sorted(folders,key=lambda p:len(p.parts),reverse=True):
        if not any(path.iterdir()):path.rmdir()
    report={'upstream_test_fixture_files_removed':len(removed),'bytes_removed':size,'files':removed}
    (ROOT/'reports/windows_payload_pruning.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if __name__=='__main__':main()
