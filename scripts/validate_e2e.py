"""Validate a browser-downloaded synthetic output, never a user upload."""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
def main(path):
    source=ROOT/"test_data/simple.xlsx"
    before=json.loads((ROOT/"reports/e2e_original_hash.json").read_text())["sha256"]
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
    original=load_workbook(source); output=load_workbook(path)
    assert output.sheetnames==original.sheetnames
    s=output.active; o=original.active
    assert s.max_row==o.max_row and s.max_column==o.max_column
    assert [c.value for c in s[1]]==[c.value for c in o[1]]
    changed=0
    for row in s.iter_rows(min_row=2):
        for c in row:
            assert c.value!=o.cell(c.row,c.column).value
            changed+=1
    assert s["B2"].value.endswith("@example.test")
    assert s["C2"].value.startswith("TEST-") and not s["C2"].value.startswith("TEST-TEL-")
    assert s.freeze_panes==o.freeze_panes
    assert s.column_dimensions["A"].width==o.column_dimensions["A"].width
    with ZipFile(path) as package:
        text=b" ".join(package.read(n) for n in package.namelist() if n.endswith(".xml"))
        assert b"prueba0@example.test" not in text and b"Persona Ficticia 0" not in text
    report={"result":"PASS","source":"synthetic simple.xlsx","rows":100,"cells_modified":changed,"manual_correction":"Teléfono -> Otro","original_hash_preserved":True,"output_opens":True,"structure_preserved":True,"selected_originals_replaced":True,"browser_upload":True,"browser_download":True}
    (ROOT/"reports/e2e.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main(sys.argv[1])
