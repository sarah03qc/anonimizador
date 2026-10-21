"""Build-only assets, runtime-license collection and integrity snapshot."""
from pathlib import Path
from importlib import metadata
from packaging.requirements import Requirement
from PIL import Image,ImageDraw
import hashlib,json,shutil,sys

ROOT=Path(__file__).resolve().parents[1]
def runtime_distributions():
    roots=['presidio-analyzer','transformers','torch','streamlit','openpyxl','Faker','defusedxml','psutil','pillow','PyYAML']
    names=set();pending=list(roots)
    while pending:
        name=pending.pop();d=metadata.distribution(name);name=d.metadata['Name']
        if name in names:continue
        names.add(name)
        for raw in d.requires or []:
            requirement=Requirement(raw)
            if requirement.marker is None or requirement.marker.evaluate({'extra':''}):pending.append(requirement.name)
    return sorted(names,key=str.lower)

def main():
    assets=ROOT/'windows/assets';assets.mkdir(exist_ok=True)
    # Native geometric artwork; no institutional emblem or generated logo.
    im=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((40,14,200,239),radius=17,fill='#663366')
    d.polygon([(156,14),(200,58),(156,58)],fill='#FF6633')
    for y in (70,96,122):d.rounded_rectangle((65,y,139,y+9),radius=4,fill='white')
    d.rounded_rectangle((122,148,230,237),radius=14,fill='#009999',outline='white',width=5)
    d.arc((142,109,210,191),180,360,fill='#009999',width=16)
    d.ellipse((167,176,185,194),fill='white');d.rectangle((173,187,179,210),fill='white')
    im.save(assets/'anonimizador.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    im.save(assets/'anonimizador.png')
    resources=ROOT/'build/windows/resources';resources.mkdir(parents=True,exist_ok=True)
    names=runtime_distributions();(resources/'runtime_distributions.json').write_text(json.dumps(names,indent=2))
    licenses=resources/'LICENSES';licenses.mkdir(exist_ok=True)
    inventory=[]
    for name in names:
        dist=metadata.distribution(name);copied=[]
        for file in dist.files or []:
            if any(word in file.name.casefold() for word in ('license','licence','copying','notice','copyright')) and dist.locate_file(file).is_file():
                relative=Path(str(file))
                # Restrict to installed distribution-owned files, avoid traversal.
                if '..' in relative.parts:continue
                destination=licenses/name/relative;destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(dist.locate_file(file),destination);copied.append(str(relative))
        inventory.append({'name':name,'version':dist.version,'license':dist.metadata.get('License-Expression') or dist.metadata.get('License','See bundled notices'),'files':copied})
    shutil.copytree(ROOT/'licenses',licenses/'application_notices',dirs_exist_ok=True)
    shutil.copytree(ROOT/'windows/notices',licenses/'upstream_notices',dirs_exist_ok=True)
    shutil.copy2(ROOT/'models/spanish-pii/README.md',licenses/'OpenMed_MODEL_CARD.md')
    python_license=Path(sys.base_prefix)/'LICENSE.txt'
    if not python_license.is_file():raise RuntimeError('Python redistribution license missing')
    shutil.copy2(python_license,licenses/'Python_LICENSE.txt')
    (licenses/'inventory.json').write_text(json.dumps(inventory,indent=2,ensure_ascii=False),encoding='utf-8')
    (resources/'THIRD_PARTY_LICENSES.txt').write_text('AVISOS DE TERCEROS\n\nLos componentes conservan sus licencias y avisos en LICENSES.\nEl inventario incluye nombres, versiones y archivos de licencia.\nOpenMed y EuroBERT: Apache-2.0. Pesos sin modificaciones.\nPyInstaller: GPL con excepción de distribución del bootloader; ver LICENSES/PyInstaller.\nNo se incluye logotipo institucional.\n',encoding='utf-8')
    # PyInstaller bootloader redistribution notice (build dependency, not runtime Python).
    pyi=metadata.distribution('pyinstaller')
    for file in pyi.files or []:
        if 'copying' in file.name.lower() or 'license' in file.name.lower():
            source=pyi.locate_file(file)
            if source.is_file():
                dest=licenses/'PyInstaller'/Path(str(file));dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    snapshot={str(p.relative_to(ROOT)):hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in [ROOT/'app.py',*sorted((ROOT/'anonymizer').glob('*.py')),*sorted((ROOT/'tests').glob('test_*.py'))]}
    (resources/'functional_baseline.json').write_text(json.dumps(snapshot,indent=2))
    print(f'Prepared generic icon and notices for {len(names)} runtime distributions.')
if __name__=='__main__':main()
