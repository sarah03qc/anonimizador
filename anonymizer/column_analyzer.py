from collections import Counter
from .header_analyzer import header_kind, normalize
from .models import Column
from .presidio_engine import ENTITY_KIND
import re

def sample(values,n=24):
    if len(values)<=n: return values
    return [values[round(i*(len(values)-1)/(n-1))] for i in range(n)]

def analyze_column(detector,sheet,index,header,values):
    kind=header_kind(header)
    nonempty=[v for v in values if v is not None and str(v).strip()]
    sampled=sample(nonempty)
    text=[str(v) for v in sampled]
    # Strong typed headers avoid expensive NER; structured recognizers still run.
    ner=kind in ("No determinado","Texto con PII") and not all(re.fullmatch(r"[\d .,-]+",t) for t in text)
    spans=detector.batch(text,header,use_ner=ner)
    hits=sum(bool(s) for s in spans)
    types=Counter(ENTITY_KIND[s.entity_type] for group in spans for s in group)
    state="No detectada como sensible"; confidence="Baja"; selected=False
    reason="Sin indicadores en la muestra. Revise el contexto."
    if kind=="Institucional":
        confidence="Alta"; reason="Encabezado de estructura institucional."
        strong=any(s.entity_type in ("EMAIL_ADDRESS","PHONE_NUMBER") for group in spans for s in group)
        if strong: state="Revisar"; confidence="Media"; reason="El contenido contradice el encabezado institucional."
    elif kind not in ("No determinado","Texto con PII"):
        state="Sensible"; confidence="Alta"; selected=True; reason="Encabezado asociado a información personal."
    elif hits:
        state="Sensible"; selected=True; confidence="Media"; reason="Se encontraron entidades en la muestra."
        kind="Texto con PII" if kind=="Texto con PII" or any(len(t)>65 or len(s)>1 for t,s in zip(text,spans)) else types.most_common(1)[0][0]
    elif kind=="Texto con PII" or normalize(header) in ("id","codigo","numero","valor","datos","fecha","edad") or not header or any(isinstance(v,str) and v.strip() for v in sampled):
        state="Revisar"; reason="Columna ambigua o texto que necesita revisión humana."
        if kind=="No determinado": kind="Otro" if normalize(header)=="edad" else kind
    return Column(sheet,index,header,state,kind,confidence,selected,hits,len(sampled),len(values),reason)
