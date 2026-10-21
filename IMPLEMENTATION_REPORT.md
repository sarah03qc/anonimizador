CEN-CINAI ANONYMIZER IMPLEMENTATION REPORT

INFORME HISTÓRICO de la implementación inicial. La arquitectura vigente y sus verificaciones se documentan en HUMAN_REVIEW.md y reports/HUMAN_REVIEW_IMPLEMENTATION_REPORT.md. Las métricas iniciales del NER se mantienen como antecedente; no determinan la sustitución de columnas estructuradas confirmadas.

Project root:
<carpeta del proyecto>

Python:
3.12.2, Windows x64.

Architecture:
Prototipo local funcional con revisión humana, Presidio, NER español, heurísticas, generadores sintéticos, openpyxl y Streamlit. NO listo para datos reales: calidad de entidades insuficiente.

Presidio:
version 2.2.364. Recognizers explícitos y adaptador EntityRecognizer para NER por lotes; no se auto-descargan modelos spaCy.

Spanish NER:
OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1. Revisión eb499b1b8349c606ca425b6d0f57777ae4ba79ff. Transformers 5.20.2, PyTorch 2.14.1, CPU Windows; sin trust_remote_code. Compatible para ejecución; calidad FAIL.

NER license:
Apache-2.0 según ficha del editor. Ver THIRD_PARTY_LICENSES.md y licenses/APACHE-2.0.txt.

NER model size:
847.310.224 bytes de pesos; 211.824.460 parámetros F32.

Estimated model RAM:
Presupuesto recomendado: 4 GB para el proceso y equipo con 8 GB. Sonda: aproximadamente 673 MiB residentes del proceso, no memoria exclusiva del modelo. Pico del benchmark final: aproximadamente 842 MiB. La presión de memoria puede causar paginación y demoras.

Faker locale:
es_MX. es_CR no está disponible en Faker 40.43.0; nombres y direcciones de es_MX probados. Identificadores, correos y teléfonos usan generadores propios explícitos de prueba.

UI framework:
Streamlit 1.66.0. Flujo en español; algunos controles internos del framework siguen en inglés. Sin certificación WCAG completa.

Processing:
LOCAL ONLY.

Internet required during anonymization:
NO. Descargas públicas solo durante instalación/desarrollo.

Supported formats:
.xlsx exclusivamente.

DETECTION

Header analysis:
PASS.

Spanish NER:
FAIL en calidad de detección; carga e inferencia compatibles.

CR recognizers:
PASS: teléfono CR, cédula y DIMEX con contexto, IBAN CR. No validan identidades oficiales.

Hybrid detection:
PASS como integración funcional; calidad de entidades FAIL.

GOLDEN DATASET

Entity precision:
35,29 % (motor híbrido, tipo y límites exactos).

Entity recall:
54,55 %.

Entity F1:
42,86 %.

Column precision:
100 %.

Column recall:
100 %.

Column F1:
100 %.

Spanish evaluation:
FAIL. 11 textos ficticios, 11 entidades y 17 columnas: conjunto pequeño de regresión, no validación institucional. NER solo: precision 14,29 %, recall 18,18 %, F1 16 %. No se cambió de modelo ni se maquillaron resultados.

ANONYMIZATION

Consistent pseudonyms within run:
PASS por tipo compatible y valor normalizado; incluye varias hojas.

Persistent mapping:
NO.

Workbook preservation:

Sheets:
PASS, incluidas ocultas.

Sheet order:
PASS.

Styles:
PARTIAL: estilos básicos probados; características fuera del alcance se rechazan.

Formulas:
PARTIAL: fórmulas compatibles conservadas, sin recálculo por openpyxl. Constantes personales y referencias/literales no admitidos se rechazan.

Merged cells:
PASS.

Column widths:
PASS.

Freeze panes:
PASS.

Original preserved:
PASS; hash intacto en E2E.

SECURITY

External transmission:
NO durante procesamiento.

PII in logs:
NO en el flujo revisado y pruebas realizadas.

Persistent uploads:
NO. La descarga elegida por la usuaria sí se guarda mediante el navegador.

Temporary cleanup:
PASS: entrada/salida de procesamiento en memoria; mapping/caché se limpian incluso ante error.

Localhost only:
PASS; escucha observada en 127.0.0.1:8501.

Offline anonymization:
PASS con modelo real y conexiones externas bloqueadas.

Security review:
PASS con notas. Revisión independiente y diez reproducciones posteriores a correcciones; límites en reports/security_review.md.

TESTS

Automated:
67/67 PASS.

E2E:
PASS: navegador real, carga, análisis, cambio manual, confirmación, 400 celdas sustituidas, descarga, apertura con openpyxl, estructura y original intactos, nuevo proceso. Revisión y recálculo manual en Microsoft Excel pendientes.

PERFORMANCE

Small:
analysis 1,46 s; anonymization 3,18 s; 100 filas.

Medium:
analysis 20,80 s; anonymization 36,24 s; 5.000 filas.

Large:
NOT_RUN.

Cifras de una ejecución con modelo cargado; no incluyen imports ni son garantía. La primera carga completa de bibliotecas puede tardar minutos en este equipo.

DEPENDENCIES

pip check:
PASS.

pip-audit:
PASS: cero avisos conocidos después de actualizar dependencias afectadas. Detalle inicial y final conservados.

WINDOWS

setup_windows.ps1:
PASS en el entorno actual; instalación limpia en otro equipo no probada.

run_windows.bat:
PASS; apertura automática del navegador confirmada por el lanzador.

Daily use requires terminal:
NO comandos; doble clic, manteniendo abierta la ventana del lanzador.

Standalone:
NOT_ATTEMPTED. Se mantiene instalación local más lanzador; EXE único no recomendado por ahora.

DOCUMENTATION

README:
PASS.

User instructions:
PASS.

Security/privacy:
PASS.

Technical limitations:
PASS.

Third-party licenses:
PASS: inventario, avisos instalados, ficha del modelo y texto Apache-2.0.

Files created:
app.py; anonymizer/; tests/; test_data/; scripts/; .streamlit/config.toml; requirements*.txt; model_manifest.json; documentación; instaladores; licenses/; reports/; .venv/; models/spanish-pii/. Inventario en reports/FILES_CREATED.md.

Files modified outside project root:
Caché automática de pip del perfil de Windows durante la instalación inicial. Descarga sintética creada por el navegador en Downloads y trasladada a reports/e2e_output.xlsx. No se modificaron otros proyectos; no se guardaron uploads reales.

Known limitations:
Recuperación y precisión de entidades insuficientes; solo evaluación ficticia. Muestreo, tablas por hoja, encabezados/nombres conservados, exclusiones OOXML, fórmulas sin recálculo, sustituciones de prueba no válidas para registros oficiales, inicio lento, controles internos de Streamlit en inglés y sin auditoría WCAG completa. Sin garantía de borrado forense de RAM ni control de OneDrive/descargas del navegador.

Gate 1:
PASS_WITH_NOTES.

Gate 2:
FAIL.

Gate 3:
PASS_WITH_NOTES.

Gate 4:
PASS_WITH_NOTES.

Gate 5:
FAIL para datos reales. Flujo técnico probado con datos ficticios.

How Alina launches it:
Doble clic en run_windows.bat. En esta versión, usar únicamente archivos ficticios.

OVERALL:
FAIL como herramienta lista para datos reales. Prototipo funcional, probado y documentado para evaluación sintética.

NEXT RECOMMENDED ACTION:
Corregir o sustituir explícitamente el NER tras una evaluación comparativa con licencia apta, ampliar el conjunto etiquetado y repetir el Gate 2 antes de un piloto con datos reales. No se hizo commit ni push.
