"""Generate only new, exclusively fictitious human-review QA fixtures."""
from pathlib import Path
import hashlib,json
from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/"test_data/human_review";folder.mkdir(exist_ok=True)
def save(name,headers,rows):
    w=Workbook();s=w.active;s.title="Datos";s.append(headers)
    for row in rows:s.append(row)
    s.freeze_panes="A2"
    for c in s[1]:s.column_dimensions[c.column_letter].width=25
    w.save(folder/name)
save("unknown_headers.xlsx",["campo_a","campo_b","dato1","dato2","detalle","valor"],[
    ["Persona Ficticia Alfa","1-2345-6789","8888-1234","alfa@example.test","dato de prueba",12],
    ["Qzxv","2-3456-7890","8777-4321","beta@example.test","nota ficticia",24],
    [None,None,None,None,"sin datos",0]])
save("review_e2e.xlsx",["Nombre","Cédula","Correo","Región","Establecimiento","campo_x","Observaciones"],[
    ["Persona Ficticia Alfa","1-2345-6789","alfa@example.test","Región ficticia","CEN ficticio","N.","Nota con información ficticia desconocida"],
    ["Persona Ficticia Alfa","2-3456-7890","beta@example.test","Región ficticia","CEN ficticio","N.","Segunda nota sintética"],
    [None,None,None,"Región ficticia","CEN ficticio",None,None]])
(ROOT/"reports/human_review_source_hashes.json").write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob("*.xlsx")},indent=2))
print("Generated two synthetic human-review fixtures.")
