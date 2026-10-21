import re
from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer, RecognizerResult
from .header_analyzer import normalize

class ContextualCRRecognizer(EntityRecognizer):
    def __init__(self, entity, pattern, context):
        super().__init__(supported_entities=[entity], supported_language="es", name=entity)
        self.entity=entity; self.pattern=re.compile(pattern); self.context=context
    def load(self): pass
    def analyze(self,text,entities,nlp_artifacts=None):
        if self.entity not in entities: return []
        results=[]
        for m in self.pattern.finditer(text):
            near=normalize(text[max(0,m.start()-70):m.start()])
            if re.search(self.context,near):
                results.append(RecognizerResult(self.entity,m.start(),m.end(),.9))
        return results

def recognizers():
    return [
        PatternRecognizer(supported_entity="EMAIL_ADDRESS",supported_language="es",patterns=[Pattern("email",r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?![\w-])",.95)]),
        PatternRecognizer(supported_entity="PHONE_NUMBER",supported_language="es",patterns=[Pattern("CR_PHONE_NUMBER",r"(?<!\w)(?:\+?506[ .-]?)?[24678]\d{3}[ .-]?\d{4}(?!\w)",.85)]),
        ContextualCRRecognizer("CR_NATIONAL_ID",r"(?<!\w)[1-9][ -]?\d{4}[ -]?\d{4}(?!\w)",r"\b(cedula|identificacion|documento|id persona)\b"),
        ContextualCRRecognizer("CR_DIMEX",r"(?<!\w)\d{11,12}(?!\w)",r"\b(dimex|residencia|identificacion extranjero)\b"),
        PatternRecognizer(supported_entity="FINANCIAL",supported_language="es",patterns=[Pattern("CR_IBAN",r"\bCR\d{2}(?:[ ]?\d){18}\b",.95)]),
        PatternRecognizer(supported_entity="PERSON",supported_language="es",global_regex_flags=re.UNICODE,patterns=[Pattern("contextual_person",r"(?<=[mM]adre )[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3}",.8),Pattern("parent_person",r"(?<=[pP]adre )[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3}",.8)])
    ]
