"""Independent XLSX oracle for actual browser downloads from the frozen EXE."""
from pathlib import Path
from io import BytesIO
from datetime import datetime
from copy import copy
import hashlib,json,sys
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
def validate(case,download):
    report_name='windows_bundle_e2e.json' if case=='review' else 'windows_zip_e2e.json'
    startup_name='windows_clean_validation.json' if case=='review' else 'windows_zip_validation.json'
    runtime=json.loads((ROOT/'reports'/startup_name).read_text(encoding='utf-8-sig'))
    assert runtime['probe']['result']=='PASS' and runtime['startup']['frozen']
    assert runtime['probe']['external_connection_denied']
    assert str(ROOT) not in runtime['startup']['executable']
    assert all(str(ROOT) not in p and '.venv' not in p for p in runtime['startup']['sys_path'])
    if case=='review':
        source=ROOT/'test_data/human_review/review_e2e.xlsx';selected={1,2,3,6,7}
        expected=json.loads((ROOT/'reports/human_review_source_hashes.json').read_text())[source.name]
    else:
        source=ROOT/'test_data/simple.xlsx';selected={1,2,3,4}
        expected=json.loads((ROOT/'reports/e2e_original_hash.json').read_text())['sha256']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
    original=load_workbook(source);output=load_workbook(download)
    assert original.sheetnames==output.sheetnames
    o=original.active;s=output.active
    assert (s.max_row,s.max_column)==(o.max_row,o.max_column)
    assert [c.value for c in s[1]]==[c.value for c in o[1]]
    count=0
    for row in o.iter_rows(min_row=2):
        for c in row:
            out=s.cell(c.row,c.column)
            if c.column in selected and c.value is not None and str(c.value).strip():
                assert out.value!=c.value;count+=1
                if case=='review' and c.column==7:assert out.value=='[CONTENIDO ANONIMIZADO]'
            else:assert out.value==c.value
            assert copy(out.font)==copy(c.font) and out.number_format==c.number_format
    assert s.freeze_panes==o.freeze_panes
    if case=='review':
        assert count==10 and s['A2'].value==s['A3'].value and s['F2'].value==s['F3'].value
    else:
        assert count==400 and isinstance(s['D2'].value,datetime) and s['C2'].value.startswith('TEST-TEL-')
    report={'result':'PASS','case':case,'runtime_executable':runtime['startup']['executable'],
        'outside_development_tree':True,'frozen_python':True,'browser_upload_review_confirm_anonymize_download':True,
        'offline_guard_active':True,'xlsx_opens':True,'original_sha256_unchanged':True,
        'structure_and_styles_preserved':True,'cells_changed':count,'selected_columns':len(selected),
        'native_excel_opened':False}
    (ROOT/'reports'/report_name).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':validate(sys.argv[1],sys.argv[2])
