# Anonimizador CEN-CINAI

Herramienta local e independiente para revisar información sensible de un Excel y producir una copia con sustituciones sintéticas. No depende de otro repositorio ni de sistemas institucionales. No requiere servicios cloud.

**Estado: detección asistida y anonimización con revisión humana obligatoria.** El sistema propone; la persona confirma. Una columna estructurada confirmada se sustituye completamente sin NER, salvo vacíos y fórmulas compatibles conservadas. El detector de entidades mantiene su evaluación insuficiente: precision 35,29 %, recall 54,55 %, F1 42,86 % (NER solo: recall 18,18 %). En texto libre, use el reemplazo completo cuando no pueda aceptar omisiones. Un piloto real requiere autorización institucional, revisión exhaustiva y validación de la copia; no equivale a aprobación para difusión.

## Instalación en Windows

Para la entrega a personas no técnicas, use la distribución **portable Windows**: extraiga la carpeta completa del ZIP y abra **Anonimizador CEN-CINAI.exe**. No requiere Python, comandos ni Internet durante el uso. Siga el `LEAME.txt` incluido. Las instrucciones siguientes corresponden al **entorno de desarrollo**, no al usuario final. Consulte [empaquetado y validación Windows](WINDOWS_DISTRIBUTION.md).

Requisito: Windows x64 y Python 3.12 de python.org, disponible para el usuario. Una persona técnica ejecuta `setup_windows.ps1` dentro de esta carpeta. El instalador crea `.venv`, instala las versiones fijadas, descarga el modelo en `models/spanish-pii` y ejecuta comprobaciones. La primera instalación necesita Internet y espacio para bibliotecas y pesos. No se instala nada globalmente ni se necesita editar configuración.

Si PowerShell restringe scripts, la persona técnica puede iniciar una sesión con `powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1` tras revisar el archivo. No se cambia la política permanente del equipo.

## Uso cotidiano

Doble clic en **run_windows.bat**. El navegador abre **http://127.0.0.1:8501**. Cargar .xlsx, revisar las hojas y sus encabezados, corregir columnas/tipos, confirmar revisión, anonimizar y descargar. Ver [INSTRUCCIONES_USUARIO.md](INSTRUCCIONES_USUARIO.md).

## Arquitectura

Streamlit sigue cinco pasos: carga, análisis, revisión y confirmación, anonimización y descarga. openpyxl lee una copia en memoria y conserva las características básicas del libro. El análisis combina nombres de columnas normalizados, muestras distribuidas, patrones Presidio y NER español local. Sus resultados solo generan defaults. Todas las columnas están disponibles para revisión; las amarillas requieren Anonimizar o Conservar explícitos. La casilla de revisión y CONFIRMAR SELECCIÓN generan una decisión inmutable ligada al hash del archivo y las filas de encabezados. Cualquier edición invalida esa confirmación y la copia anterior.

El modelo solicitado se mantiene: **OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1**, revisión **eb499b1b8349c606ca425b6d0f57777ae4ba79ff**, Apache-2.0. La implementación nativa EuroBERT de Transformers evita `trust_remote_code`. Se integra como `EntityRecognizer` de Presidio. No se descarga un segundo modelo spaCy. Las etiquetas de nombres se traducen a PERSON, contacto a EMAIL_ADDRESS/PHONE_NUMBER, direcciones a LOCATION, nacimiento a DATE_OF_BIRTH, identificadores a ID, credenciales a CREDENTIAL y cuentas a FINANCIAL. Etiquetas genéricas de fechas, montos, moneda, ocupación y organizaciones no bastan por sí solas para anonimizar.

La sustitución usa Faker español y generadores explícitos de prueba. Un diccionario efímero mantiene consistencia entre hojas. Las columnas estructuradas confirmadas sustituyen todos los valores literales no vacíos con su tipo, sin invocar NER. Texto libre ofrece detección por entidades (puede omitir PII) o reemplazo completo por `[CONTENIDO ANONIMIZADO]`. Se conservan fórmulas compatibles y se solicita recálculo al abrir Excel. El servicio de la UI usa `anonymize_reviewed`; `anonymize` se conserva como API interna de bajo nivel para compatibilidad y requiere que su llamador gestione la revisión.

Los módulos `anonymizer/review.py` y `anonymizer/profiles.py` separan decisiones humanas de recomendaciones. Los perfiles YAML utilizan coincidencias exactas de encabezados normalizados, solo configuran defaults y nunca confirman. El único perfil incluido es **SYNTHETIC_DEMO_PROFILE**, exclusivamente ficticio. Consulte [HUMAN_REVIEW.md](HUMAN_REVIEW.md).

## Desarrollo y verificación

El código fuente y los artefactos de entrega se mantienen separados: `build/`, `dist/`, `release/`, `models/`, `.venv/`, cachés y reportes generados están excluidos de Git. Los binarios grandes y el modelo no deben añadirse al historial normal. Para preparar el modelo local en desarrollo, ejecute `setup_windows.ps1`; también puede usar `.venv\Scripts\python.exe scripts\install_model.py` tras instalar las dependencias. La descarga verifica la revisión e integridad fijadas en el proyecto. Para construir, instale `requirements-build.txt` y ejecute `scripts/build_windows.ps1` en Windows x64. No se publica nada automáticamente.

Todos los comandos se ejecutan desde esta raíz usando `.venv\Scripts\python.exe`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\generate_test_data.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\evaluate.py
.\.venv\Scripts\python.exe scripts\benchmark.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pip_audit
```

`test_data` contiene únicamente libros ficticios. `reports` contiene resultados reproducibles, no archivos personales. La configuración operativa está en `.streamlit/config.toml`. Los límites están en `anonymizer/workbook.py`. No se usan DataFrames para reconstruir libros.

## Funcionamiento sin Internet

Después de instalar, el modelo se carga con `local_files_only=True`; no se utiliza inference API. El lanzador desactiva telemetría y establece modo offline. La aplicación bloquea conexiones de sockets fuera del loopback. Las pruebas ejecutan carga real del modelo y una anonimización con conexiones de red bloqueadas. No hay fuentes, imágenes, scripts ni analítica externos en la interfaz.

## Resolución de problemas

- **Falta Python:** instalar Python 3.12 x64; después ejecutar setup_windows.ps1.
- **Descarga interrumpida:** repetir instalador. Las descargas del instalador usan un archivo parcial y comprobación posterior del modelo.
- **Instalación pendiente:** el lanzador no inicia hasta completar las comprobaciones.
- **Puerto ocupado:** cerrar la otra instancia de la herramienta y volver a abrir. No conectarse a servidores ajenos.
- **Excel rechazado:** consultar el mensaje; puede haber protección, contenido externo, formatos no admitidos o límites excedidos. No se quitan contraseñas.
- **Inicio lento:** la primera carga del modelo puede demorar. Consultar el benchmark del equipo.
- **Carpeta movida:** volver a ejecutar instalador para reconstruir el entorno virtual; no copiar una `.venv` entre equipos.

## Documentación

- [Plan de arquitectura y fuentes](ARCHITECTURE_PLAN.md)
- [Seguridad y privacidad](SECURITY_PRIVACY.md)
- [Límites técnicos](TECHNICAL_LIMITATIONS.md)
- [Licencias](THIRD_PARTY_LICENSES.md)

No se garantiza detección perfecta ni irreversibilidad. La salida requiere revisión humana antes de compartirla. No utilizar registros reales en las pruebas de desarrollo.
