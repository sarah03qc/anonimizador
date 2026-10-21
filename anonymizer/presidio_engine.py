from presidio_analyzer import EntityRecognizer, RecognizerResult
from .cr_recognizers import recognizers
from .header_analyzer import normalize
import re

ENTITY_KIND={"PERSON":"Persona","EMAIL_ADDRESS":"Correo","PHONE_NUMBER":"Teléfono","LOCATION":"Dirección / ubicación","DATE_OF_BIRTH":"Fecha personal","CR_NATIONAL_ID":"Identificación","CR_DIMEX":"Identificación","ID":"Identificación","FINANCIAL":"Financiero","CREDENTIAL":"Credencial"}

class OpenMedRecognizer(EntityRecognizer):
    def __init__(self,ner):
        self.ner=ner
        super().__init__(supported_entities=list(ENTITY_KIND),supported_language="es",name="OpenMedSpanishLocal")
    def load(self): pass
    def analyze(self,text,entities,nlp_artifacts=None):
        return [r for r in self.ner.batch([text])[0] if r.entity_type in entities]
    def analyze_batch(self,texts):
        return self.ner.batch(texts)

def resolve(text,spans):
    # Merge adjacent person parts from FIRSTNAME/LASTNAME before overlap resolution.
    people=sorted([s for s in spans if s.entity_type=="PERSON"],key=lambda s:(s.start,-s.end))
    merged=[]
    for s in people:
        if merged and 0<=s.start-merged[-1].end<=2 and text[merged[-1].end:s.start].isspace():
            merged[-1]=RecognizerResult("PERSON",merged[-1].start,s.end,min(s.score,merged[-1].score))
        else: merged.append(s)
    candidates=merged+[s for s in spans if s.entity_type!="PERSON"]
    chosen=[]
    for s in sorted(candidates,key=lambda s:(-(s.end-s.start),-s.score,s.start)):
        if not any(s.start<t.end and t.start<s.end for t in chosen): chosen.append(s)
    return sorted(chosen,key=lambda s:s.start)

class Detector:
    """Explicit Presidio recognizers, no auto-loading/default network providers."""
    def __init__(self,ner):
        self.ner_recognizer=OpenMedRecognizer(ner)
        self.patterns=recognizers()
        self.cache={}

    def batch(self,texts,header="",use_ner=True):
        missing=list(dict.fromkeys(t for t in texts if (header,t,use_ner) not in self.cache))
        predicted=self.ner_recognizer.analyze_batch(missing) if use_ner else [[] for _ in missing]
        for text,spans in zip(missing,predicted):
            # NER labels must not bypass the contextual restriction on numeric IDs.
            context=normalize(header+" "+text)
            spans=[s for s in spans if not (s.entity_type=="ID" and re.fullmatch(r"[\d -]{9,}",text[s.start:s.end]) and not re.search(r"\b(cedula|dimex|identificacion|documento|pasaporte|ssn)\b",context))]
            prefix=header+": " if header else ""
            for recognizer in self.patterns:
                for s in recognizer.analyze(prefix+text,recognizer.supported_entities):
                    if s.start>=len(prefix): spans.append(RecognizerResult(s.entity_type,s.start-len(prefix),s.end-len(prefix),s.score))
            self.cache[header,text,use_ner]=resolve(text,spans)
        return [self.cache[header,t,use_ner] for t in texts]

    def clear(self): self.cache.clear()
