"""Exact typed-span metrics on a deliberately small independent synthetic fixture."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from anonymizer.privacy import block_external_network
block_external_network()
from anonymizer.spanish_ner import SpanishNER
from anonymizer.presidio_engine import Detector,resolve
from anonymizer.column_analyzer import analyze_column

def metrics(tp,fp,fn):
    p=tp/(tp+fp) if tp+fp else 0; r=tp/(tp+fn) if tp+fn else 0
    return {"tp":tp,"fp":fp,"fn":fn,"precision":p,"recall":r,"f1":2*p*r/(p+r) if p+r else 0}

def score(golden,predictions):
    tp=fp=fn=0
    for case,pred in zip(golden,predictions):
        expected={(a,b,t) for a,b,t in case["entities"]}
        found={(s.start,s.end,s.entity_type) for s in pred}
        tp+=len(expected&found); fp+=len(found-expected); fn+=len(expected-found)
    return metrics(tp,fp,fn)

def main():
    data=json.loads((ROOT/"test_data/golden.json").read_text(encoding="utf-8")); cases=data["entities"]
    ner=SpanishNER(); detector=Detector(ner)
    texts=[r["text"] for r in cases]
    hybrid=detector.batch(texts)
    raw=[resolve(t,s) for t,s in zip(texts,ner.batch(texts))]
    cols=[analyze_column(detector,"Evaluación",i+1,c["header"],c["values"]) for i,c in enumerate(data["columns"])]
    tp=fp=fn=0
    for c,g in zip(cols,data["columns"]):
        pred=c.state=="Sensible"; expected=g["sensitive"]
        tp+=int(pred and expected); fp+=int(pred and not expected); fn+=int(not pred and expected)
    results={"method":"Exact entity type and character span; PERSON adjacent parts merged. Column positive = Sensible; Revisar is not positive.","cases":len(cases),"columns":len(cols),"hybrid_entity":score(cases,hybrid),"ner_only_entity":score(cases,raw),"column":metrics(tp,fp,fn),"limitations":"Small regression fixture, not representative institutional validation. No inference of general accuracy.","case_counts":[{"case":i+1,"expected":len(g["entities"]),"hybrid_detected":len(h),"ner_detected":len(n)} for i,(g,h,n) in enumerate(zip(cases,hybrid,raw))]}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports/evaluation.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    detector.clear(); print(json.dumps(results,indent=2))

if __name__=="__main__": main()
