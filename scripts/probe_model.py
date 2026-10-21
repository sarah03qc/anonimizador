"""Installation-time compatibility probe. Uses only synthetic text."""
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1")

def main():
    import importlib.metadata as meta
    import torch
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    from faker import Faker
    from faker.config import AVAILABLE_LOCALES
    import psutil
    from presidio_analyzer import Pattern, PatternRecognizer
    start = time.perf_counter()
    p = str(ROOT / "models" / "spanish-pii")
    tokenizer = AutoTokenizer.from_pretrained(p, local_files_only=True, trust_remote_code=False)
    model = AutoModelForTokenClassification.from_pretrained(p, local_files_only=True, trust_remote_code=False, attn_implementation="eager")
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    ner = pipeline("token-classification", model=model, tokenizer=tokenizer, aggregation_strategy="simple", device=-1)
    loaded = time.perf_counter() - start
    examples = ["La madre María Rodríguez llamó al 8888-1234 y escribió a maria@example.test.", "José Andrés Muñoz vive en San José, Alajuela.", "María José Peña Quesada"]
    start = time.perf_counter()
    outputs = ner(examples, batch_size=4)
    recognizer = PatternRecognizer(supported_entity="EMAIL_ADDRESS", supported_language="es", patterns=[Pattern("email", r"\b[\w.+-]+@[\w.-]+\.\w+\b", .9)])
    assert recognizer.analyze(examples[0], ["EMAIL_ADDRESS"])
    locale = "es_CR" if "es_CR" in AVAILABLE_LOCALES else "es_MX"
    fake = Faker(locale)
    assert fake.name() and fake.address()
    data = {"versions": {x: meta.version(x) for x in ["presidio-analyzer", "transformers", "torch", "Faker", "streamlit", "openpyxl"]}, "locale": locale, "locales_es": [x for x in AVAILABLE_LOCALES if x.startswith("es")], "load_seconds": loaded, "inference_seconds": time.perf_counter()-start, "rss_mb": psutil.Process().memory_info().rss / 1024**2, "model_bytes": (Path(p)/"model.safetensors").stat().st_size, "labels": model.config.id2label, "synthetic_results": [[{"type": e["entity_group"], "start": e["start"], "end": e["end"], "score": float(e["score"])} for e in out] for out in outputs]}
    (ROOT/"reports").mkdir(exist_ok=True)
    (ROOT/"reports"/"model_probe.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
