"""Network access belongs ONLY to installation. No user workbooks here."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1"
REVISION = "eb499b1b8349c606ca425b6d0f57777ae4ba79ff"
FILES = ["config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "README.md", "model.safetensors"]

def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source,"sha256").hexdigest()

def main():
    dest = ROOT / "models" / "spanish-pii"
    dest.mkdir(parents=True, exist_ok=True)
    expected=json.loads((ROOT/"model_manifest.json").read_text(encoding="utf-8"))["sha256"]
    hashes = {}
    for name in FILES:
        path = dest / name
        if not path.exists() or digest(path)!=expected[name]:
            print(f"Descargando {name}...", flush=True)
            partial = path.with_suffix(path.suffix + ".partial")
            try:
                urllib.request.urlretrieve(f"https://huggingface.co/{MODEL}/resolve/{REVISION}/{name}", partial)
                if digest(partial)!=expected[name]:
                    raise RuntimeError("La descarga no coincide con la integridad fijada del modelo.")
                partial.replace(path)
            finally:
                partial.unlink(missing_ok=True)
        hashes[name] = expected[name]
    (dest / "manifest.json").write_text(json.dumps({"model": MODEL, "revision": REVISION, "sha256": hashes}, indent=2), encoding="utf-8")
    print("Modelo local descargado. Se verificará con una inferencia sin Internet.")

if __name__ == "__main__":
    main()
