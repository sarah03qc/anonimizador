from dataclasses import dataclass, field

KINDS = ["Persona", "Identificación", "Teléfono", "Correo", "Dirección / ubicación", "Fecha personal", "Financiero", "Credencial", "Texto con PII", "Otro", "Institucional", "No determinado"]

@dataclass
class Column:
    sheet: str
    index: int
    header: str
    state: str
    kind: str
    confidence: str
    selected: bool = False
    matches: int = 0
    sampled: int = 0
    rows: int = 0
    reason: str = ""

@dataclass
class Analysis:
    columns: list[Column]
    seconds: float
    sheets: int
    rows: int
    warnings: list[str] = field(default_factory=list)

@dataclass
class Result:
    data: bytes
    filename: str
    seconds: float
    cells: int
    columns: int
    sheets: int
    counts: dict
