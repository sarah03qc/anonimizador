"""QA installation only: freeze baseline and download public candidate assets."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/gate2"
MODELS={"piiranha":"iiiorg/piiranha-v1-detect-personal-information","beto":"gpancardo/beto-pii"}

def digest(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()

def baseline():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=[ROOT/"app.py",ROOT/"run_windows.bat",ROOT/"scripts/launch.py",ROOT/"anonymizer/workbook.py",ROOT/"anonymizer/service.py",ROOT/"anonymizer/replacement.py",ROOT/"anonymizer/pseudonym_map.py"]
    paths+=list((ROOT/"tests").glob("test_*.py"))
    paths+=list((ROOT/"anonymizer").glob("*.py"))
    data={str(p.relative_to(ROOT)):digest(p) for p in paths}
    (OUT/"baseline_hashes.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
    for p in (ROOT/"anonymizer").glob("*.py"):
        target=OUT/"baseline_code"/p.name; target.parent.mkdir(exist_ok=True);target.write_bytes(p.read_bytes())
    (OUT/"baseline_evaluation.json").write_bytes((ROOT/"reports/evaluation.json").read_bytes())

def download(key,repo):
    info=json.load(urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}",timeout=60))
    revision=info["sha"]; dest=ROOT/"models/candidates"/key;dest.mkdir(parents=True,exist_ok=True)
    allowed={"config.json","tokenizer.json","tokenizer_config.json","special_tokens_map.json","added_tokens.json","vocab.txt","spm.model","sentencepiece.bpe.model","model.safetensors","README.md","LICENSE","LICENSE.txt"}
    names=[x["rfilename"] for x in info["siblings"] if x["rfilename"] in allowed]
    record={"repo":repo,"revision":revision,"license":info.get("cardData",{}).get("license"),"files":{}}
    def fetch(name):
        p=dest/name
        if not p.exists():
            partial=p.with_suffix(p.suffix+".partial")
            print(f"{key}: {name}",flush=True)
            urllib.request.urlretrieve(f"https://huggingface.co/{repo}/resolve/{revision}/{name}",partial)
            partial.replace(p)
        return name,{"sha256":digest(p),"bytes":p.stat().st_size}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        record["files"]=dict(pool.map(fetch,names))
    (dest/"manifest.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(key,"READY",revision,record["license"],flush=True)

if __name__=="__main__":
    import sys
    if "--baseline" in sys.argv:baseline()
    if "--download" in sys.argv:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda x:download(*x),MODELS.items()))
    if "--reference" in sys.argv:
        dest=OUT/"openmed_reference";dest.mkdir(parents=True,exist_ok=True)
        for name in ["configuration_eurobert.py","modeling_eurobert.py"]:
            urllib.request.urlretrieve("https://huggingface.co/OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1/resolve/eb499b1b8349c606ca425b6d0f57777ae4ba79ff/"+name,dest/name)
