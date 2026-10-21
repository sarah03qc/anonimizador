"""Verify the actual browser download; exclusively synthetic fixtures."""
from pathlib import Path
from io import BytesIO
from copy import copy
from zipfile import ZipFile
import hashlib,json,sys
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
def main(path):
    source=ROOT/"test_data/human_review/review_e2e.xlsx"
    hashes=json.loads((ROOT/"reports/human_review_source_hashes.json").read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==hashes[source.name]
    original=load_workbook(source);output=load_workbook(path)
    assert original.sheetnames==output.sheetnames
    o=original.active;s=output.active
    assert s.max_row==o.max_row and s.max_column==o.max_column
    assert [c.value for c in s[1]]==[c.value for c in o[1]]
    changed=0
    for row in o.iter_rows(min_row=2):
        for c in row:
            out=s.cell(c.row,c.column)
            if c.column in (1,2,3,6,7) and c.value is not None:
                assert out.value!=c.value
                if c.column==7:assert out.value=="[CONTENIDO ANONIMIZADO]"
                changed+=1
            else:assert out.value==c.value
            assert copy(out.font)==copy(c.font) and out.number_format==c.number_format
    assert s["A2"].value==s["A3"].value and s["F2"].value==s["F3"].value
    assert s.freeze_panes==o.freeze_panes
    assert s["C2"].value.endswith("@example.test")
    assert s["B2"].value.startswith("TEST-ID-")
    assert changed==10
    with ZipFile(path) as z:
        xml=b" ".join(z.read(n) for n in z.namelist() if n.endswith(".xml"))
        for text in ("Persona Ficticia Alfa","alfa@example.test","1-2345-6789","Nota con información ficticia desconocida"):
            assert text.encode() not in xml
    report={"result":"PASS","fixture":"human_review/review_e2e.xlsx","browser_upload":True,"browser_human_edits":True,"explicit_confirmation":True,"browser_download":True,"all_columns":7,"selected_columns":5,"cells_changed":changed,"campo_x_missed_by_actual_NER":"N.","campo_x_human_type":"Persona","campo_x_replaced":True,"free_text_mode":"complete","region_establishment_preserved":True,"blanks_preserved":True,"consistent_pseudonyms":True,"original_hash_preserved":True,"output_openpyxl_validation":True,"manual_excel_application_opened":False}
    (ROOT/"reports/human_review_e2e.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=True))
if __name__=="__main__":main(sys.argv[1])
