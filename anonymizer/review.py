"""Human review is the authority. Stores metadata/choices only, in memory."""
from collections import Counter
from dataclasses import dataclass,replace
import hashlib

STRUCTURED="Reemplazo estructurado completo"
ENTITIES="Detectar y sustituir entidades"
COMPLETE="Reemplazar contenido completo"
PRESERVE="Conservar"
PENDING="Pendiente"
METHODS=(STRUCTURED,ENTITIES,COMPLETE,PRESERVE)
REVIEW_TYPES=("Persona","Identificación","Teléfono","Correo","Dirección / ubicación","Fecha personal","Financiero","Credencial / usuario","Texto libre","Otro sensible","Institucional","Conservar","No determinado")
TO_ENGINE={"Persona":"Persona","Identificación":"Identificación","Teléfono":"Teléfono","Correo":"Correo","Dirección / ubicación":"Dirección / ubicación","Fecha personal":"Fecha personal","Financiero":"Financiero","Credencial / usuario":"Credencial","Texto libre":"Texto con PII","Otro sensible":"Otro"}
FROM_ENGINE={v:k for k,v in TO_ENGINE.items()}

class ReviewError(ValueError):pass

@dataclass(frozen=True)
class ReviewRow:
    sheet:str
    index:int
    header:str
    automatic_state:str
    kind:str
    confidence:str
    selected:bool
    method:str
    resolution:str
    matches:int=0
    sampled:int=0
    rows:int=0
    source:str="Detección automática"
    automatic_kind:str=""

    @property
    def key(self):return self.sheet,self.index

@dataclass(frozen=True)
class ConfirmedReview:
    workbook_sha256:str
    header_rows:tuple
    decisions:tuple[ReviewRow,...]

def default_method(kind):
    if kind=="Texto libre":return ENTITIES
    if kind in ("Conservar","Institucional","No determinado"):return PRESERVE
    return STRUCTURED

def build_review(columns):
    return [ReviewRow(c.sheet,c.index,c.header,c.state,FROM_ENGINE.get(c.kind,c.kind),c.confidence,c.selected,default_method(FROM_ENGINE.get(c.kind,c.kind)),PENDING if c.state=="Revisar" else "Anonimizar" if c.selected else PRESERVE,c.matches,c.sampled,c.rows,automatic_kind=c.kind) for c in columns]

def edit_row(row,*,selected=None,kind=None,method=None,resolution=None):
    """Explicit UI actions reconcile checkbox and yellow decision in one place."""
    new_kind=row.kind if kind is None else kind
    new_selected=row.selected if selected is None else bool(selected)
    new_method=row.method if method is None else method
    new_resolution=row.resolution if resolution is None else resolution
    if kind is not None and new_kind!=row.kind:
        if method is None:new_method=default_method(new_kind)
        if new_kind=="Conservar":new_selected=False;new_resolution=PRESERVE;new_method=PRESERVE
    if selected is not None:
        new_resolution="Anonimizar" if new_selected else PRESERVE
        if new_selected and new_method==PRESERVE and method is None:new_method=default_method(new_kind)
        if not new_selected:new_method=PRESERVE
    if resolution in ("Anonimizar",PRESERVE):
        new_selected=resolution=="Anonimizar"
        if not new_selected:new_method=PRESERVE
        elif new_method==PRESERVE and method is None:new_method=default_method(new_kind)
    return replace(row,selected=new_selected,kind=new_kind,method=new_method,resolution=new_resolution,source="Decisión humana")

def merge_editor(row,edited):
    fields={}
    for column,attribute in [("Anonimizar","selected"),("Tipo","kind"),("Método","method"),("Resolver revisión","resolution")]:
        if edited[column]!=getattr(row,attribute):fields[attribute]=edited[column]
    return edit_row(row,**fields) if fields else row

def automatic_label(row):
    if row.automatic_state=="Revisar":return "🟡 Revisar"
    if row.automatic_state=="Sensible":return "🔴 Sensible"
    if row.automatic_kind=="Institucional":return "🔵 Institucional"
    return "🟢 Sin indicadores detectados"

def ordered(rows):
    def rank(r):
        return 0 if r.automatic_state=="Sensible" else 1 if r.automatic_state=="Revisar" else 3 if r.automatic_kind=="Institucional" else 2
    return sorted(rows,key=lambda r:(rank(r),r.index))

def visible_rows(rows,view):
    predicates={"Todas":lambda r:True,"Seleccionadas":lambda r:r.selected,"Requieren revisión":lambda r:r.automatic_state=="Revisar","Sin indicadores":lambda r:r.automatic_state not in ("Sensible","Revisar") and r.automatic_kind!="Institucional","Institucionales":lambda r:r.automatic_kind=="Institucional"}
    return [r for r in ordered(rows) if predicates[view](r)]

def editor_records(rows):
    return [{"Anonimizar":r.selected,"Hoja":r.sheet,"N.º":r.index,"Columna":r.header or "Sin encabezado","Detección":automatic_label(r),"Tipo":r.kind,"Confianza":r.confidence,"Método":r.method,"Resolver revisión":r.resolution,"Filas":r.rows,"Coincidencias":r.matches,"Muestra":r.sampled} for r in rows]

def validation_errors(rows,expected_keys=None):
    errors=[];keys=[r.key for r in rows]
    if len(keys)!=len(set(keys)) or expected_keys is not None and set(keys)!=set(expected_keys):
        errors.append("La revisión debe incluir todas las columnas de todas las hojas, sin duplicados.")
    pending=sum(r.automatic_state=="Revisar" and r.resolution==PENDING for r in rows)
    if pending:errors.append(f"Hay {pending} columnas que requieren revisión antes de continuar. Elija Anonimizar o Conservar.")
    for r in rows:
        if r.kind not in REVIEW_TYPES or r.method not in METHODS:errors.append("Hay un tipo o método de revisión no válido.");break
        if r.resolution not in (PENDING,"Anonimizar",PRESERVE):errors.append("Hay una decisión de revisión no válida.");break
        if r.resolution in ("Anonimizar",PRESERVE) and r.selected!=(r.resolution=="Anonimizar"):
            errors.append("La selección y la decisión de revisión deben coincidir.");break
        if r.selected:
            if r.kind not in TO_ENGINE:errors.append("Asigne un tipo de información a cada columna seleccionada.");break
            if r.method==PRESERVE:errors.append("Elija un método de anonimización para cada columna seleccionada.");break
            if r.kind=="Texto libre" and r.method not in (ENTITIES,COMPLETE):errors.append("Para texto libre, elija detectar entidades o reemplazar contenido completo.");break
            if r.kind!="Texto libre" and r.method!=STRUCTURED:errors.append("Las columnas estructuradas deben usar reemplazo estructurado completo.");break
    if not any(r.selected for r in rows):errors.append("Seleccione al menos una columna para anonimizar.")
    return list(dict.fromkeys(errors))

def confirm_review(rows,columns,data,header_rows,attested=False):
    if not attested:raise ReviewError("Confirme que ha revisado todas las columnas antes de continuar.")
    errors=validation_errors(rows,[(c.sheet,c.index) for c in columns])
    if errors:raise ReviewError(errors[0])
    return ConfirmedReview(hashlib.sha256(data).hexdigest(),tuple(sorted(header_rows.items())),tuple(rows))

def validate_confirmation(plan,data):
    if not isinstance(plan,ConfirmedReview):raise ReviewError("Debe confirmar la selección antes de anonimizar.")
    if plan.workbook_sha256!=hashlib.sha256(data).hexdigest():raise ReviewError("El archivo cambió. Vuelva a revisar y confirmar las columnas.")
    errors=validation_errors(plan.decisions)
    if errors:raise ReviewError(errors[0])

def summary(rows):return dict(Counter(r.kind for r in rows if r.selected))
