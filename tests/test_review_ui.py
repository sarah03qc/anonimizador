"""Streamlit integration checks: mandatory decisions and stale-output invalidation."""
from io import BytesIO
from pathlib import Path
import hashlib
import pytest
from openpyxl import Workbook
import streamlit as st
from streamlit.testing.v1 import AppTest
from anonymizer.models import Analysis,Column
from anonymizer.review import build_review

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def ui(monkeypatch):
    w=Workbook();w.active.title="Datos"
    w.active.append(["Nombre","Monto","Observaciones"])
    w.active.append(["Persona ficticia",12,"Nota ficticia"])
    b=BytesIO();w.save(b)
    class Upload:
        name="synthetic-ui.xlsx"
        def getvalue(self):return b.getvalue()
    upload=Upload()
    monkeypatch.setattr(st,"file_uploader",lambda *a,**k:upload)
    columns=[Column("Datos",1,"Nombre","Sensible","Persona","Alta",True),
             Column("Datos",2,"Monto","No detectada como sensible","No determinado","Baja",False),
             Column("Datos",3,"Observaciones","Revisar","Texto con PII","Baja",False)]
    app=AppTest.from_file(str(ROOT/"app.py"),default_timeout=30)
    app.session_state["digest"]=hashlib.sha256(upload.getvalue()+upload.name.encode()).hexdigest()
    app.session_state["headers_signature"]=(('Datos',1),)
    app.session_state["analysis"]=Analysis(columns,0,1,1)
    app.session_state["review_rows"]=build_review(columns)
    app.run()
    assert not app.exception
    return app

def element(app,kind,label):
    return next(e for e in getattr(app,kind) if e.label==label)

def resolve_yellow(app):
    element(app,"selectbox","Columna a ajustar").set_value(3).run()
    element(app,"selectbox","Decisión").set_value("Conservar")
    element(app,"button","Aplicar decisión de columna").click().run()
    assert not app.exception

def confirm(app):
    element(app,"checkbox","He revisado todas las columnas y confirmé cuáles deben anonimizarse.").check().run()
    element(app,"button","CONFIRMAR SELECCIÓN").click().run()
    assert not app.exception

def test_ui_yellow_blocks_even_with_global_checkbox(ui):
    element(ui,"checkbox","He revisado todas las columnas y confirmé cuáles deben anonimizarse.").check().run()
    assert element(ui,"button","CONFIRMAR SELECCIÓN").disabled
    assert element(ui,"button","ANONIMIZAR ARCHIVO").disabled

def test_ui_explicit_confirm_after_yellow_resolution(ui):
    resolve_yellow(ui)
    assert element(ui,"button","ANONIMIZAR ARCHIVO").disabled
    confirm(ui)
    assert not element(ui,"button","ANONIMIZAR ARCHIVO").disabled
    assert not ui.session_state["plan"].decisions[2].selected

def test_ui_edits_invalidate_confirmation_and_output(ui):
    resolve_yellow(ui);confirm(ui)
    ui.session_state["result"]=object() # Must be removed before result rendering.
    element(ui,"selectbox","Tipo de información").set_value("Correo")
    element(ui,"selectbox","Decisión").set_value("Anonimizar")
    element(ui,"selectbox","Método de sustitución").set_value("Según el tipo")
    element(ui,"button","Aplicar decisión de columna").click().run()
    assert not ui.exception
    assert "plan" not in ui.session_state and "result" not in ui.session_state
    assert not ui.session_state["attested"]
    assert element(ui,"button","ANONIMIZAR ARCHIVO").disabled

def test_ui_filters_keep_hidden_yellow_blocking(ui):
    element(ui,"radio","Mostrar columnas").set_value("Sin indicadores").run()
    assert len(ui.session_state["review_rows"])==3
    assert element(ui,"button","CONFIRMAR SELECCIÓN").disabled
    assert any("requieren revisión" in w.value for w in ui.warning)
