"""Local UI. No uploads, cell values or mappings are persisted or logged."""
from anonymizer.privacy import block_external_network
block_external_network()

import hashlib
import streamlit as st
from anonymizer import workbook
from pathlib import Path
from anonymizer.review import (build_review, visible_rows, editor_records, merge_editor, edit_row,
    validation_errors, confirm_review, summary, REVIEW_TYPES, METHODS, PENDING, PRESERVE,
    ENTITIES, COMPLETE, default_method, ReviewError)
from anonymizer.profiles import load_profile, apply_profile, suggest_profiles

st.set_page_config(page_title="CEN-CINAI · Anonimizador",page_icon="🔒",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
.block-container {max-width:1150px; padding-top:2rem;}
h1,h2,h3 {color:#663366;}
.privacy {border-left:5px solid #007777;background:#edf8f7;padding:1rem 1.2rem;border-radius:8px;margin:1rem 0 1.5rem; color:#18413e;}
.brand {letter-spacing:.12em;font-size:1rem;font-weight:800;color:#663366;}
.stButton button[kind=primary] {min-height:3rem;font-weight:700;}
button:focus-visible {outline:3px solid #a04016!important;outline-offset:3px;}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="brand">CEN-CINAI</div>',unsafe_allow_html=True)
st.title("Anonimizador de archivos")
st.write("Proteja información sensible antes de utilizar datos para análisis, pruebas o desarrollo.")
st.markdown('<div class="privacy"><strong>🔒 Procesamiento local</strong><br>El archivo se procesa únicamente en este equipo y no se envía a Internet.</div>',unsafe_allow_html=True)
st.info("Las selecciones automáticas son una ayuda. Revise todas las columnas antes de continuar. El sistema propone; la persona confirma.")
st.caption("Herramienta de detección asistida y anonimización con revisión humana. Valide la copia antes de compartirla en un entorno autorizado.")

@st.cache_resource(show_spinner=False)
def get_ner():
    from anonymizer.spanish_ner import SpanishNER
    return SpanishNER()

def reset():
    epoch=st.session_state.get("epoch",0)+1
    st.session_state.clear(); st.session_state["epoch"]=epoch

def invalidate_review():
    for key in ("plan","result"):st.session_state.pop(key,None)
    st.session_state.attested=False
    st.session_state.review_version=st.session_state.get("review_version",0)+1

def update_review(rows):
    invalidate_review()
    st.session_state.review_rows=rows

def revoke_confirmation():
    for key in ("plan","result"):st.session_state.pop(key,None)

def review_columns(analysis,metadata):
    st.header("3. Revise las columnas",divider="gray")
    st.write("Hemos seleccionado automáticamente las columnas que podrían contener información sensible. Revise la lista completa antes de continuar. Puede agregar o quitar columnas y cambiar el tipo de información detectada.")
    rows=st.session_state.review_rows
    a,b,c=st.columns(3)
    a.metric("🔴 Potencialmente sensibles",sum(r.automatic_state=="Sensible" for r in rows))
    b.metric("🟡 Requieren revisión",sum(r.automatic_state=="Revisar" and r.resolution==PENDING for r in rows))
    c.metric("🟢 Sin indicadores detectados",sum(r.automatic_state not in ("Sensible","Revisar") and r.automatic_kind!="Institucional" for r in rows))
    st.caption("Se incluyen todas las hojas y columnas, también las ocultas. Las coincidencias corresponden a una muestra de hasta 24 valores por columna; no se muestran contenidos de celdas.")
    with st.expander("Perfiles de columnas · opcional"):
        profile=load_profile(Path(__file__).parent/"profiles/synthetic_demo_profile.yaml")
        st.write(profile.name+" — "+profile.description)
        if suggest_profiles(analysis.columns,[profile]):st.info("Los encabezados coinciden con el perfil sintético de demostración.")
        if st.button("Aplicar defaults del perfil sintético"):
            update_review(apply_profile(rows,profile));st.rerun()
    view=st.radio("Mostrar columnas",["Todas","Seleccionadas","Requieren revisión","Sin indicadores","Institucionales"],horizontal=True)
    version=st.session_state.get("review_version",0)
    for i,(sheet,_,_,state) in enumerate(metadata):
        with st.expander(sheet+(" (oculta)" if state!="visible" else ""),expanded=True):
            shown=visible_rows([r for r in rows if r.sheet==sheet],view)
            if not shown:st.caption("No hay columnas que coincidan con este filtro.");continue
            edited=st.data_editor(editor_records(shown),key=f"editor_{i}_{version}_{view}",hide_index=True,use_container_width=True,
                disabled=["Hoja","N.º","Columna","Detección","Confianza","Filas","Coincidencias","Muestra"],
                column_order=["Anonimizar","Columna","Detección","Tipo","Método","Resolver revisión","Confianza","Hoja","N.º","Filas","Coincidencias","Muestra"],
                column_config={"Anonimizar":st.column_config.CheckboxColumn("Anonimizar"),"Tipo":st.column_config.SelectboxColumn("Tipo",options=REVIEW_TYPES,required=True),"Método":st.column_config.SelectboxColumn("Método",options=METHODS,required=True),"Resolver revisión":st.column_config.SelectboxColumn("Resolver revisión",options=[PENDING,"Anonimizar",PRESERVE],required=True)})
            changes={r.key:merge_editor(r,e) for r,e in zip(shown,edited)}
            merged=[changes.get(r.key,r) for r in rows]
            if merged!=rows:update_review(merged);st.rerun()
            # An accessible alternative to editing a wide grid, including on small screens.
            with st.expander("Ajustar una columna con controles",expanded=True):
                chosen=st.selectbox("Columna a ajustar",[r.index for r in shown],format_func=lambda n:next(r.header or f"Columna {n}" for r in shown if r.index==n),key=f"choose_{i}_{version}_{view}")
                r=next(r for r in shown if r.index==chosen)
                with st.form(f"adjust_{i}_{version}_{chosen}_{view}"):
                    decision=st.selectbox("Decisión",[PENDING,"Anonimizar",PRESERVE],index=[PENDING,"Anonimizar",PRESERVE].index(r.resolution))
                    kind=st.selectbox("Tipo de información",REVIEW_TYPES,index=REVIEW_TYPES.index(r.kind))
                    method=st.selectbox("Método de sustitución",["Según el tipo",*METHODS],index=METHODS.index(r.method)+1 if r.selected else 0,help="En texto libre, el reemplazo completo elimina toda la celda y sacrifica su información. Si cambia a un tipo estructurado, elija Según el tipo o Reemplazo estructurado completo.")
                    if st.form_submit_button("Aplicar decisión de columna"):
                        record=editor_records([r])[0]
                        record.update({"Tipo":kind,"Método":default_method(kind) if method=="Según el tipo" else method,"Resolver revisión":decision})
                        changed=merge_editor(r,record)
                        update_review([changed if x.key==r.key else x for x in rows]);st.rerun()
    st.warning("La detección dentro de texto libre es automática y puede no identificar todos los datos sensibles. Modo conservador: reemplazar contenido completo. Esta opción sustituye cada celda no vacía por [CONTENIDO ANONIMIZADO] y elimina el contenido útil de la nota.")
    st.caption("Columnas estructuradas confirmadas: se sustituyen todos los valores literales no vacíos, sin consultar al NER. Las fórmulas compatibles se conservan; revise sus resultados, los encabezados y los nombres de hojas.")
    errors=validation_errors(rows,[(c.sheet,c.index) for c in analysis.columns])
    for error in errors:st.warning(error)
    attested=st.checkbox("He revisado todas las columnas y confirmé cuáles deben anonimizarse.",key="attested",on_change=revoke_confirmation)
    if st.button("CONFIRMAR SELECCIÓN",disabled=bool(errors) or not attested,use_container_width=True):
        st.session_state.plan=confirm_review(rows,analysis.columns,st.session_state.current_data,dict(st.session_state.headers_signature),attested=True)
    if "plan" in st.session_state:st.success("Selección confirmada. Cualquier cambio exige una nueva confirmación.")

def main():
    st.header("1. Seleccione su archivo",divider="gray")
    upload=st.file_uploader("Arrastre su archivo Excel o búsquelo en el equipo (.xlsx)",type=["xlsx"],key=f"upload_{st.session_state.get('epoch',0)}",help="Hasta 50 MiB. Solo .xlsx, sin contraseña ni objetos externos.")
    if upload is None: return
    data=upload.getvalue(); digest=hashlib.sha256(data+upload.name.encode("utf-8")).hexdigest()
    if st.session_state.get("digest")!=digest:
        for k in list(st.session_state):
            if k not in ("epoch",) and not k.startswith("upload_"): del st.session_state[k]
        st.session_state.digest=digest
    try:
        wb=workbook.load(data,upload.name)
        metadata=[(ws.title,ws.max_row,ws.max_column,ws.sheet_state) for ws in wb]; wb.close()
    except workbook.WorkbookError as exc:
        st.error(str(exc)); return
    except Exception:
        st.error("No fue posible abrir el archivo."); return
    st.write(f"Archivo: **{upload.name}**")
    a,b,c=st.columns(3); a.metric("Tamaño",f"{len(data)/1024**2:.2f} MiB"); b.metric("Hojas",len(metadata)); c.metric("Filas aproximadas",sum(max(0,r-1) for _,r,_,_ in metadata))
    header_rows={}
    with st.expander("Revise las hojas y su fila de encabezados",expanded=False):
        st.write("Una tabla por hoja. También se incluyen hojas, filas y columnas ocultas. Compruebe que los nombres de hojas y encabezados no contienen información personal.")
        for i,(name,rows,cols,state) in enumerate(metadata):
            label=f"{name} · {rows} filas · {cols} columnas"+(" · hoja oculta" if state!="visible" else "")
            header_rows[name]=int(st.number_input("Fila de encabezados: "+label,min_value=1,max_value=max(1,min(50,rows)),value=1,step=1,key=f"header_{i}"))
    signature=tuple(header_rows.items())
    if st.session_state.get("headers_signature")!=signature:
        for key in ["analysis","result","plan","review_rows","attested"]:
            st.session_state.pop(key,None)
        for key in list(st.session_state):
            if key.startswith("editor_"): del st.session_state[key]
        st.session_state.headers_signature=signature
    st.header("2. Analice la información",divider="gray")
    reanalyze=st.button("ANALIZAR INFORMACIÓN SENSIBLE",use_container_width=False)
    if "analysis" not in st.session_state or reanalyze:
        invalidate_review()
        try:
            with st.spinner("Analizando localmente. La primera carga del detector puede tardar…"):
                from anonymizer.service import Service
                progress=st.progress(0,text="Analizando columnas")
                service=Service(get_ner())
                st.session_state.analysis=service.analyze(data,upload.name,header_rows,lambda v:progress.progress(v))
                st.session_state.review_rows=build_review(st.session_state.analysis.columns)
                progress.empty()
        except workbook.WorkbookError as exc:
            st.error(str(exc)); return
        except Exception:
            st.error("No fue posible analizar el archivo. Compruebe que la instalación terminó correctamente y vuelva a intentarlo."); return
    analysis=st.session_state.analysis
    st.session_state.current_data=data
    review_columns(analysis,metadata)
    st.header("4. Anonimice el archivo",divider="gray")
    plan=st.session_state.get("plan")
    if plan:
        st.write(f"Se anonimizarán {sum(r.selected for r in plan.decisions)} columnas.")
        for kind,count in summary(plan.decisions).items():st.write(f"{kind}: {count}")
    else:st.caption("Revise todas las columnas y confirme su selección para habilitar este paso.")
    if st.button("ANONIMIZAR ARCHIVO",type="primary",disabled=plan is None,use_container_width=True):
        st.session_state.pop("result",None)
        try:
            with st.spinner("Generando la copia con datos ficticios…"):
                from anonymizer.service import Service
                progress=st.progress(0,text="Anonimizando columnas seleccionadas")
                st.session_state.result=Service(get_ner()).anonymize_reviewed(data,upload.name,plan,lambda v:progress.progress(v))
                progress.empty()
        except (workbook.WorkbookError,ReviewError) as exc: st.error(str(exc))
        except Exception: st.error("No fue posible completar la anonimización. Revise la instalación y vuelva a intentarlo.")
    if "result" in st.session_state:
        r=st.session_state.result
        st.header("5. Descargue el resultado",divider="gray")
        st.success("Archivo procesado correctamente. Revise la copia antes de compartirla.")
        a,b,c=st.columns(3); a.metric("Hojas con cambios",r.sheets); b.metric("Columnas seleccionadas",r.columns); c.metric("Celdas modificadas",r.cells)
        labels={"Persona":"Personas","Identificación":"Identificaciones","Teléfono":"Teléfonos","Correo":"Correos","Fecha personal":"Fechas personales","Dirección / ubicación":"Direcciones / ubicaciones","Financiero":"Datos financieros","Credencial":"Credenciales / usuarios","Otro":"Otros datos sensibles","Texto con PII":"Texto libre — entidades"}
        for kind,count in r.counts.items(): st.write(f"{labels.get(kind,kind)}: {count:,} celdas")
        st.caption(f"Análisis: {analysis.seconds:.1f} s · Sustitución: {r.seconds:.1f} s. Los teléfonos e identificadores generados son datos sintéticos y no corresponden a personas reales.")
        st.download_button("DESCARGAR ARCHIVO ANONIMIZADO",r.data,file_name=r.filename,mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary",use_container_width=True)
    st.button("Procesar otro archivo",on_click=reset)

main()
