# Build with the pinned PyInstaller and hooks in requirements-build.txt.
from pathlib import Path
from importlib import metadata
from PyInstaller.utils.hooks import collect_data_files,collect_submodules,copy_metadata

root=Path(SPECPATH).parent
datas=[(str(root/'app.py'),'.'),(str(root/'.streamlit'),'.streamlit'),
    (str(root/'profiles'),'profiles'),(str(root/'models/spanish-pii'),'models/spanish-pii'),
    (str(root/'windows/assets'),'assets')]
for package in ('streamlit','presidio_analyzer','spacy','thinc','transformers','tokenizers','safetensors','huggingface_hub'):
    datas+=collect_data_files(package)
# Metadata for installed runtime distributions, never development tools.
import json
import sys
sys.setrecursionlimit(max(sys.getrecursionlimit(),5000))
runtime=json.loads((root/'build/windows/resources/runtime_distributions.json').read_text())
for name in runtime:
    datas+=copy_metadata(name)
hidden=['anonymizer.service','anonymizer.spanish_ner','anonymizer.review','anonymizer.profiles',
    'streamlit.web.bootstrap','streamlit.runtime.scriptrunner.magic_funcs',
    'transformers.models.eurobert.configuration_eurobert','transformers.models.eurobert.modeling_eurobert',
    'transformers.models.auto.configuration_auto','transformers.models.auto.modeling_auto',
    'transformers.models.auto.tokenization_auto','transformers.tokenization_utils_tokenizers',
    'transformers.tokenization_utils_base','transformers.pipelines.token_classification']
hidden+=collect_submodules('presidio_analyzer')
hidden+=collect_submodules('streamlit',filter=lambda n:'.testing' not in n and '.hello' not in n)
hidden+=collect_submodules('transformers.models.eurobert')
hidden+=collect_submodules('spacy.lang.es')
a=Analysis([str(root/'windows/launcher.py')],pathex=[str(root)],binaries=[],datas=datas,
    hiddenimports=hidden,hookspath=[str(root/'windows/hooks')],runtime_hooks=[],
    excludes=['pytest','pip_audit','IPython','notebook','jupyter','matplotlib','tensorflow','jax','torchaudio','torchvision','tests'],
    noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='Anonimizador CEN-CINAI',
    debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False,
    icon=str(root/'windows/assets/anonimizador.ico'),contents_directory='_internal')
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='Anonimizador_CEN-CINAI')
