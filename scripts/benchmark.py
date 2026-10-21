import json
import platform
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from anonymizer.privacy import block_external_network
block_external_network()
from anonymizer.spanish_ner import SpanishNER
from anonymizer.service import Service
import psutil

def main():
    service=Service(SpanishNER()); results={"platform":platform.platform(),"processor":platform.processor(),"logical_cpus":psutil.cpu_count(),"total_ram_mb":psutil.virtual_memory().total/1024**2,"runs":{}}
    for label,name in [("small","simple.xlsx"),("medium","realista.xlsx")]:
        data=(ROOT/"test_data"/name).read_bytes()
        a=service.analyze(data,name)
        selected={(c.sheet,c.index):c.kind for c in a.columns if c.selected}
        r=service.anonymize(data,name,selected)
        results["runs"][label]={"rows":a.rows,"analysis_seconds":a.seconds,"anonymization_seconds":r.seconds,"cells_modified":r.cells,"rss_after_mb":psutil.Process().memory_info().rss/1024**2}
        print(label,results["runs"][label],flush=True)
    results["peak_working_set_mb"]=getattr(psutil.Process().memory_info(),"peak_wset",0)/1024**2
    results["large"]="NOT_RUN"
    (ROOT/"reports/benchmark.json").write_text(json.dumps(results,indent=2),encoding="utf-8")

if __name__=="__main__":main()
