from pathlib import Path
from threading import RLock
import os

from .privacy import offline_environment

LABEL_MAP = {}
for labels, entity in [
    ("FIRSTNAME LASTNAME MIDDLENAME", "PERSON"),
    ("EMAIL", "EMAIL_ADDRESS"), ("PHONE", "PHONE_NUMBER"),
    ("STREET CITY STATE COUNTY ZIPCODE SECONDARYADDRESS BUILDINGNUMBER GPSCOORDINATES", "LOCATION"),
    ("DATEOFBIRTH", "DATE_OF_BIRTH"),
    ("SSN IMEI VIN VRM MASKEDNUMBER", "ID"),
    ("BANKACCOUNT IBAN CREDITCARD CREDITCARDISSUER CVV BIC BITCOINADDRESS ETHEREUMADDRESS LITECOINADDRESS", "FINANCIAL"),
    ("USERNAME PASSWORD PIN ACCOUNTNAME IPADDRESS MACADDRESS USERAGENT URL", "CREDENTIAL"),
]:
    for label in labels.split(): LABEL_MAP[label]=entity

class SpanishNER:
    def __init__(self):
        offline_environment()
        import torch
        from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
        torch.set_num_threads(min(4,os.cpu_count() or 1))
        path=str(Path(__file__).resolve().parents[1]/"models"/"spanish-pii")
        tokenizer=AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        model=AutoModelForTokenClassification.from_pretrained(path, local_files_only=True, trust_remote_code=False, attn_implementation="eager")
        self.pipe=pipeline("token-classification",model=model,tokenizer=tokenizer,aggregation_strategy="simple",device=-1)
        self.lock=RLock()

    def batch(self,texts):
        """Bounded overlapping character windows; offsets refer to original text."""
        from presidio_analyzer import RecognizerResult
        windows=[]; refs=[]
        for i,text in enumerate(texts):
            for start in range(0,len(text),700):
                windows.append(text[start:start+1000]); refs.append((i,start))
                if start+1000>=len(text): break
        result=[[] for _ in texts]
        if not windows: return result
        with self.lock:
            outputs=self.pipe(windows,batch_size=8)
        for output,(i,offset) in zip(outputs,refs):
            for e in output:
                entity=LABEL_MAP.get(e["entity_group"])
                if entity and float(e["score"])>=.55:
                    result[i].append(RecognizerResult(entity_type=entity,start=offset+e["start"],end=offset+e["end"],score=float(e["score"])))
        return result
