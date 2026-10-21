from datetime import date,datetime
from uuid import uuid4
from faker import Faker
from faker.config import AVAILABLE_LOCALES
from .pseudonym_map import PseudonymMap
from .presidio_engine import ENTITY_KIND, resolve
from presidio_analyzer import RecognizerResult
import re

LOCALE="es_CR" if "es_CR" in AVAILABLE_LOCALES else "es_MX"

class Replacer:
    def __init__(self):
        self.fake=Faker(LOCALE); self.mapping=PseudonymMap(); self.known={}
    def value(self,value,kind):
        def generate():
            token=uuid4().hex[:12]
            if kind=="Persona": return self.fake.name()
            if kind=="Correo": return f"prueba.{token}@example.test"
            if kind=="Teléfono": return "TEST-TEL-"+token
            if kind=="Dirección / ubicación": return "Dirección ficticia: "+self.fake.address().replace("\n",", ")
            if kind=="Fecha personal":
                d=self.fake.date_between(start_date=date(1970,1,1),end_date=date(2020,12,31))
                return datetime.combine(d,datetime.min.time()) if isinstance(value,datetime) else d if isinstance(value,date) else d.isoformat()
            return {"Identificación":"TEST-ID-","Financiero":"TEST-FIN-","Credencial":"TEST-USR-"}.get(kind,"TEST-")+token
        return self.mapping.get(value,kind,generate)

    def remember(self,value,kind):
        if isinstance(value,str) and len(value.strip())>=3:
            self.known[value.strip()]=kind

    def text(self,text,spans):
        # Only values from selected personal fields become extra literal recognizers.
        extra=[]
        for value,kind in self.known.items():
            for m in re.finditer(r"(?<!\w)"+re.escape(value)+r"(?!\w)",text,re.I):
                entity=next((e for e,k in ENTITY_KIND.items() if k==kind),"ID")
                extra.append(RecognizerResult(entity,m.start(),m.end(),1.0))
        for s in reversed(resolve(text,list(spans)+extra)):
            text=text[:s.start]+str(self.value(text[s.start:s.end],ENTITY_KIND[s.entity_type]))+text[s.end:]
        return text

    def clear(self): self.mapping.clear(); self.known.clear()
