from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
bundle=ROOT/'dist/Anonimizador_CEN-CINAI';release=ROOT/'release';release.mkdir(exist_ok=True)
target=release/'Anonimizador_CEN-CINAI_v1.0_Windows.zip'
partial=target.with_suffix('.zip.partial')
with ZipFile(partial,'w',compression=ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for path in sorted(bundle.rglob('*')):
        if path.is_file():z.write(path,path.relative_to(bundle.parent))
with ZipFile(partial) as z:assert z.testzip() is None
partial.replace(target)
sha=hashlib.file_digest(target.open('rb'),'sha256').hexdigest()
(release/'SHA256SUMS.txt').write_text(f'{sha}  {target.name}\n',encoding='utf-8')
print(json.dumps({'zip':target.name,'bytes':target.stat().st_size,'sha256':sha,'zip_crc':'PASS'},indent=2))
