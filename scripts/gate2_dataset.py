"""Synthetic QA fixtures, frozen before tuning. No inference in this builder."""
from pathlib import Path
import hashlib
import json
from io import BytesIO
from openpyxl import Workbook

ROOT=Path(__file__).resolve().parents[1]

def annotated(parts):
    text="";entities=[]
    for part in parts:
        if isinstance(part,tuple):
            value,typ=part; start=len(text);text+=value;entities.append({"start":start,"end":len(text),"type":typ})
        else:text+=part
    return text,entities

def build(split,n,negative_count):
    # Identity vocabularies and surrounding sentence structures are disjoint by split.
    dev=split=="development"
    first=["María José","José Andrés","Ana Lucía","Carlos Eduardo","Sofía","Gabriel","Valeria","Diego","Lucía Elena","Roberto","Daniel","Fernanda","Isabel","Joaquín","Natalia","Esteban"] if dev else ["Daniela Isabel","Luis Fernando","Patricia Elena","Andrés Felipe","Camila","Mateo","Adriana","Tomás"]
    surnames=["Muñoz Quesada","Gómez Peña","Rodríguez Vargas","Solís Mora","Jiménez Castro","Rojas Méndez","Chacón Soto","Araya Núñez","López Sánchez","Vargas Ortiz","Mora Ramírez","Quirós Vega","Méndez Coto","Arias Murillo","Castro Zúñiga","Soto Gutiérrez"] if dev else ["Bolaños Ureña","Céspedes Aguilar","Hernández Porras","Calderón Zamora","Segura Brenes","Villalobos León","Salazar Acuña","Cordero Alvarado"]
    cities=["San José","Alajuela","Cartago","Heredia","Escazú","Curridabat","Desamparados","Grecia","Naranjo","Palmares","Turrialba","Siquirres","Guápiles","San Carlos","San Isidro","Puriscal"] if dev else ["Pérez Zeledón","San Ramón","Liberia","Puntarenas","Cañas","Orotina","Quepos","Nicoya"]
    families=["first","last","full","email","phone","national_id","dimex","birth","address","city","username","financial","ip","passport","mixed"]
    result=[]
    for family in families:
        for i in range(n):
            f=first[i%len(first)];s=surnames[(i*3)%len(surnames)];person=f+" "+s;city=cities[i%len(cities)]
            email=f"qa.{split}.{i}@example.test";phone=[f"8888-{7000+i:04}",f"+506 8777 {4000+i:04}",f"2466-{3000+i:04}",f"+506 7000-{6000+i:04}"][i%4]
            ident=f"1-0999-{8000+i:04}";dimex=f"19009999{2000+i:04}";birth=f"{1+i%27:02}/{1+i%12:02}/{1990+i%15}"
            address=f"Calle Ensayo {40+i}, avenida Demostración, {city}";user=f"qa_{split}_{i:03}";account=f"CR00 0000 0000 0000 00{1000+i:04}";ip=f"192.0.2.{1+i}";passport=f"QA{700000+i}"
            header=["dato","valor","campo1","detalle","informacion"][i%5]
            isolated=i%4==0
            if family=="first": parts=[(f,"PERSON")] if isolated else (["El primer nombre de la persona es ",(f,"PERSON"),"."] if dev else ["Se registró ",(f,"PERSON")," como nombre de pila."])
            elif family=="last":parts=[(s,"PERSON")] if isolated else (["Los apellidos son ",(s,"PERSON"),"."] if dev else ["En el campo de apellidos figura ",(s,"PERSON"),"."])
            elif family=="full":parts=[(person,"PERSON")] if isolated else (["La persona responsable es ",(person,"PERSON"),"."] if dev else ["Entrevistamos a ",(person,"PERSON")," para completar el registro."])
            elif family=="email":parts=[(email,"EMAIL")] if isolated else (["Enviar información al correo ",(email,"EMAIL"),"."] if dev else ["Para responder utilice ",(email,"EMAIL")," como dirección de correo electrónico."])
            elif family=="phone":parts=[(phone,"PHONE")] if isolated else (["Llame al teléfono ",(phone,"PHONE")," mañana."] if dev else ["El número de contacto anotado fue ",(phone,"PHONE"),"."])
            elif family=="national_id":parts=(["Cédula: ",(ident,"ID")] if dev else ["Se verificó la identificación personal ",(ident,"ID")," para el trámite."])
            elif family=="dimex":parts=(["DIMEX ",(dimex,"ID")] if dev else ["Documento de residencia DIMEX: ",(dimex,"ID"),"."])
            elif family=="birth":parts=(["Fecha de nacimiento: ",(birth,"DATE")] if dev else ["La persona nació el ",(birth,"DATE"),"."])
            elif family=="address":parts=(["Domicilio: ",(address,"LOCATION"),"."] if dev else ["La dirección de residencia indicada es ",(address,"LOCATION"),"."])
            elif family=="city":parts=[(city,"LOCATION")] if isolated else (["La persona reside en ",(city,"LOCATION"),"."] if dev else ["Domicilio de la persona en la ciudad de ",(city,"LOCATION"),"."])
            elif family=="username":parts=(["Usuario: ",(user,"USERNAME")] if dev else ["Su nombre de usuario para iniciar sesión es ",(user,"USERNAME"),"."])
            elif family=="financial":parts=(["IBAN de la cuenta bancaria: ",(account,"FINANCIAL")] if dev else ["La cuenta bancaria de la persona corresponde al IBAN ",(account,"FINANCIAL"),"."])
            elif family=="ip":parts=(["IP del dispositivo personal: ",(ip,"IP")] if dev else ["Se anotó como dirección IP del usuario ",(ip,"IP"),"."])
            elif family=="passport":parts=(["Pasaporte: ",(passport,"ID")] if dev else ["Documento de viaje, pasaporte ",(passport,"ID"),"."])
            else:parts=(["La madre ",(person,"PERSON")," llamó al ",(phone,"PHONE")," y dejó el correo ",(email,"EMAIL"),"."] if dev else ["Atendimos a ",(person,"PERSON"),". Para seguimiento indicó el correo ",(email,"EMAIL")," y el teléfono ",(phone,"PHONE"),"."])
            text,entities=annotated(parts)
            result.append({"id":f"{split}-{family}-{i:03}","family":family,"header":header,"text":text,"entities":entities})
    for i in range(negative_count):
        templates=[("Código establecimiento",str(1100102+i)),("Código OL",str(101+i)),("Código Región",str(1+i%9)),("Año",str(2020+i%10)),("Monto",str(125000+i*100)),("Edad",str(1+i%15)),("Consecutivo",str(123456789+i)),("Cantidad",str(10+i)),("Región",["Central","Norte","Sur","Atlántica"][i%4]),("Oficina Local","Oficina de Demostración" if dev else "Oficina de Ensayo"),("Establecimiento","Centro Puerta Azul" if dev else "Centro Río Claro"),("detalle","Se completó la revisión sin novedades." if dev else "No hay observaciones pendientes para este período."),("valor","Código establecimiento 1100102, oficina 101, región 1." if dev else "El establecimiento usa código 2200203 y la oficina tiene código 205."),("campo1",f"Año {2020+i%5}, monto {100000+i}, edad {1+i%9}."),("informacion","Número 123456789 sin contexto personal." if dev else "Consecutivo de inventario 987654321 sin identificación de personas."),("Fecha registro","2026-10-20" if dev else "2025-09-15")]
        h,t=templates[i%len(templates)]
        if i>=len(templates):t+=" "+(["Revisión completada.","Sin cambios pendientes.","Información del período.","Validación administrativa."][i//len(templates)-1] if dev else "Control de inventario.")
        result.append({"id":f"{split}-negative-{i:03}","family":"negative","header":h,"text":t,"entities":[]})
    return result

def main():
    out=ROOT/"test_data/gate2";out.mkdir(exist_ok=True)
    dev=build("development",16,80);hold=build("holdout",8,40)
    manifest={"policy":"100% synthetic. Holdout identities, phrase templates and outputs excluded from tuning. No model outputs used to construct annotations.","counts":{},"sha256":{}}
    for name,data in [("development",dev),("holdout",hold)]:
        p=out/(name+".json");p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        manifest["counts"][name]=len(data);manifest["sha256"][name]=hashlib.sha256(p.read_bytes()).hexdigest()
        for c in data:
            for e in c["entities"]:assert 0<=e["start"]<e["end"]<=len(c["text"])
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    # A separate content-driven workbook. No personal headers.
    w=Workbook();s=w.active;s.title="Sin pistas"
    headers=["campo_a","campo_b","dato1","dato2","valor","detalle","info","campo_z","dato3"]
    s.append(headers)
    for i in range(12):
        s.append(["Daniela Isabel Bolaños Ureña",f"excel.qa{i}@example.test",f"8888-{9000+i:04}",f"Cédula 1-0999-{9000+i:04}",f"DIMEX 19009999{3000+i:04}","La persona Camila Hernández dejó correo excel@example.test y teléfono 8777-4444.",1100102+i,2026,125000+i])
    w.save(out/"unknown_headers.xlsx")
    (out/"unknown_headers_expected.json").write_text(json.dumps({"sensitive_columns":[1,2,3,4,5,6],"negative_columns":[7,8,9],"note":"Identifier cells carry personal context in content; generic naked numeric identifiers remain negative."},indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":main()
