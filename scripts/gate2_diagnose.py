"""Direct Transformers vs existing integration, original synthetic golden only."""
import json
import os
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from anonymizer.privacy import block_external_network
block_external_network()
from scripts.gate2_metrics import normalize_predictions,evaluate,base,ALIASES,CONTEXT_ONLY,canonical

def main():
    import torch
    from transformers import AutoModelForTokenClassification,AutoTokenizer,pipeline
    torch.set_num_threads(4)
    p=str(ROOT/"models/spanish-pii");start=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(p,local_files_only=True,trust_remote_code=False)
    model,loading=AutoModelForTokenClassification.from_pretrained(p,local_files_only=True,trust_remote_code=False,attn_implementation="eager",output_loading_info=True)
    raw=pipeline("token-classification",model=model,tokenizer=tokenizer,device=-1,aggregation_strategy="simple")
    cases=json.loads((ROOT/"test_data/golden.json").read_text(encoding="utf-8"))["entities"]
    texts=[c["text"] for c in cases]
    tokens=raw(texts,batch_size=8,aggregation_strategy="none",ignore_labels=[])
    simple=raw(texts,batch_size=8,aggregation_strategy="simple")
    single=[raw(t,aggregation_strategy="simple") for t in texts]
    def clean(groups):return [[{k:float(v) if k=="score" else int(v) if k in ("start","end","index") else v for k,v in p.items()} for p in group] for group in groups]
    tokens=clean(tokens);simple=clean(simple);single=clean(single)
    # Reuse the exact same direct Transformers pipeline for adapter comparison.
    from anonymizer.spanish_ner import SpanishNER,LABEL_MAP
    from anonymizer.presidio_engine import Detector,resolve
    from threading import RLock
    adapter=SpanishNER.__new__(SpanishNER);adapter.pipe=raw;adapter.lock=RLock()
    integrated=adapter.batch(texts)
    def convert(groups):return [[{"start":r.start,"end":r.end,"type":canonical(r.entity_type),"score":r.score} for r in group] for group in groups]
    mapped=convert([resolve(t,s) for t,s in zip(texts,integrated)])
    detector=Detector(adapter);hybrid=convert(detector.batch(texts));detector.clear()
    audit=[]
    for idx,label in model.config.id2label.items():
        labelbase=base(label)
        audit.append({"id":int(idx),"model_label":label,"base":labelbase,"internal_entity":ALIASES.get(labelbase,"CONTEXT_ONLY" if labelbase in CONTEXT_ONLY else "OUTSIDE" if labelbase=="O" else "UNMAPPED"),"presidio_before":LABEL_MAP.get(labelbase),"disposition_before":"mapped" if labelbase in LABEL_MAP else "silently_discarded" if labelbase!="O" else "outside"})
    report={"data_policy":"Original 11 synthetic examples only; detailed text/token QA expressly authorized.","id2label":model.config.id2label,"label2id":model.config.label2id,"label_audit":audit,"loading_info":{k:str(v) for k,v in loading.items()},"load_and_run_seconds":time.perf_counter()-start,"raw_metrics":evaluate(cases,[normalize_predictions(t,g) for t,g in zip(texts,simple)]),"adapter_before_metrics":evaluate(cases,mapped),"hybrid_before_metrics":evaluate(cases,hybrid),"thresholds":{str(th):evaluate(cases,[normalize_predictions(t,g,th) for t,g in zip(texts,simple)]) for th in [.2,.3,.4,.5,.55,.6,.7,.8]},"cases":[{**c,"raw_tokens":tok,"raw_simple_batched":agg,"raw_simple_single":one,"adapter_before":ada,"hybrid_before":hyb} for c,tok,agg,one,ada,hyb in zip(cases,tokens,simple,single,mapped,hybrid)]}
    report["runtime_config"]=model.config.to_dict()
    report["tokenizer_special_ids"]={"pad":tokenizer.pad_token_id,"eos":tokenizer.eos_token_id,"bos":tokenizer.bos_token_id}
    out=ROOT/"reports/gate2/openmed_original_diagnostic.json";out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:report[k] for k in ["loading_info","raw_metrics","adapter_before_metrics","hybrid_before_metrics"]},indent=2))

if __name__=="__main__":main()
