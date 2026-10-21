import importlib.metadata as metadata
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=[]
    for dist in metadata.distributions():
        m=dist.metadata
        inventory.append({"name":m["Name"],"version":dist.version,"license_expression":m.get("License-Expression"),"license_summary":(m.get("License") or "Ver LICENSE/avisos de la distribución").splitlines()[0][:250],"license_files":[str(f) for f in dist.files or [] if "license" in str(f).lower() or "notice" in str(f).lower()]})
    (ROOT/"reports/dependency_licenses.json").write_text(json.dumps(sorted(inventory,key=lambda x:x["name"].lower()),indent=2),encoding="utf-8")
    print(f"Inventario de {len(inventory)} distribuciones guardado sin datos personales.")

if __name__=="__main__":main()
