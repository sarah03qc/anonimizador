# Revisión humana y perfiles

El sistema propone; la persona confirma. Orden de autoridad: decisión humana confirmada, defaults del perfil, reglas deterministas, encabezados, NER y heurísticas. Las recomendaciones se calculan antes de la revisión; jamás sustituyen una decisión confirmada.

## Cinco pasos para Alina

1. Abra `run_windows.bat` y cargue una copia `.xlsx`. Revise las hojas y la fila de encabezados. También se incluyen columnas y hojas ocultas.
2. Espere el análisis local. El muestreo puede omitir información; los resultados son recomendaciones.
3. Revise **todas** las columnas. Agregue columnas verdes cuando corresponda; desmarque rojas incorrectas. Elija tipo y método. Resuelva cada amarilla mediante **Anonimizar** o **Conservar**, incluso si su casilla ya está marcada. Use la tabla o **Ajustar una columna con controles**. Los filtros solo cambian lo visible: una amarilla oculta sigue bloqueando. Marque la casilla global y pulse **CONFIRMAR SELECCIÓN**.
4. Compruebe el resumen por tipos y pulse **ANONIMIZAR ARCHIVO**. Cualquier cambio exige confirmar otra vez y descarta la copia anterior.
5. Descargue y valide la copia. Revise también encabezados, nombres de hojas, fórmulas, combinaciones de variables y columnas conservadas. No sobrescriba el original.

## Métodos

- **Reemplazo estructurado completo:** persona, identificación, teléfono, correo, dirección, fecha personal, financiero, credencial/usuario y otro sensible. Cada valor literal no vacío se sustituye con el tipo confirmado. No se consulta al NER para decidir qué celda modificar. Fechas Excel mantienen datetime/date; teléfonos e identificadores usan textos con prefijos de prueba. None y cadenas vacías o de espacios se conservan. Las fórmulas compatibles se mantienen por el contrato previo de preservación y necesitan revisión aparte.
- **Texto libre — detectar y sustituir entidades:** mantiene el contexto y sustituye solo entidades detectadas por Presidio/NER/patrones o nombres completos conocidos en columnas personales seleccionadas. Puede omitir datos: precision 35,29 %, recall 54,55 %, F1 42,86 % en el pequeño conjunto inicial; NER solo recall 18,18 %.
- **Texto libre — reemplazar contenido completo:** cada literal no vacío pasa a `[CONTENIDO ANONIMIZADO]`. No usa NER y pierde toda la información de esa celda. Preferible cuando no se pueda validar cada omisión de la estrategia por entidades.

## Contrato del servicio

`confirm_review` exige atestación, decisiones válidas, resolución explícita de amarillas y cobertura de todas las columnas del análisis. Devuelve un snapshot inmutable con hash del libro y filas de encabezados. `Service.anonymize_reviewed` valida otra vez el hash, todas las columnas reales del libro, los tipos y los métodos antes de procesar. La UI invalida el snapshot y la descarga al editar. La antigua API `anonymize` permanece como motor de bajo nivel para compatibilidad con los 67 tests e integraciones; no constituye una interfaz que confirme por sí sola.

La consistencia de pseudónimos se conserva por valor normalizado y tipo compatible durante una ejecución, incluso entre hojas. No hay persistencia del mapa ni de las decisiones.

## Perfiles configurables

Solo se distribuye `profiles/synthetic_demo_profile.yaml`, llamado **SYNTHETIC_DEMO_PROFILE**, para ejemplos y pruebas. No representa el formato institucional real.

Un perfil define `name`, `description`, `required_headers` y una lista `rules`. Cada regla incluye `header`, `action` (`anonymize` o `preserve`), `type` y, opcionalmente, `sheet` y `method`. Los tipos y métodos son los mismos de la UI. Sin `sheet`, la regla utiliza `*`; una regla de hoja específica tiene prioridad. Las coincidencias de encabezados son exactas tras normalización; no hay fuzzy matching. El conjunto requerido solo sugiere perfiles, nunca los aplica silenciosamente.

Aplicar un perfil configura defaults, invalida cualquier confirmación anterior y deja pendientes las columnas amarillas. La persona puede cambiar cada default antes de confirmar. No se aprende ni guarda un perfil desde datos subidos. Un futuro perfil para Alina debe elaborarse con encabezados autorizados y ejemplos ficticios representativos, manteniendo la revisión obligatoria.

## Restos de la tarea cancelada

La comparación con `reports/gate2/baseline_hashes.json` no encontró cambios en la app, motor ni tests estables. Se conservaron los scripts y datos de QA bajo `gate2`, un diagnóstico sintético y archivos de candidatos (BETO completo y Piiranha parcial) fuera del flujo operativo. Se detuvo la descarga pendiente. El único modelo usado por la app sigue siendo OpenMed español; no se incorporaron candidatos ni nuevos benchmarks.

## Alcance de preparación

Para repetir las verificaciones: genere los fixtures nuevos con `scripts/human_review_fixtures.py` y ejecute `python -m pytest -q` desde el entorno del proyecto. En este equipo, cierre temporalmente la app al ejecutar pruebas que cargan el modelo: mantener varias copias del NER puede agotar la memoria/paginación de Windows. Esto no requiere modificar la configuración del sistema. Las pruebas de interfaz usan canales locales del sistema operativo.

Columnas estructuradas confirmadas: preparadas para el contrato de sustitución de literales, con revisión de fórmulas y metadatos. Texto libre por entidades: solo con advertencia y validación exhaustiva; no asegura eliminar toda PII. Texto libre completo: preparado para sustituir todos los literales no vacíos. Piloto real: condicionado a autorización, entorno local controlado y revisión antes de cualquier difusión. La herramienta no certifica irreversibilidad ni evita por sí sola reidentificación mediante cuasi-identificadores.
