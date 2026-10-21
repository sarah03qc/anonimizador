# CEN-CINAI ANONYMIZER ARCHITECTURE PLAN

Actualización de arquitectura: la implementación vigente requiere revisión humana y confirmación explícita; ver [HUMAN_REVIEW.md](HUMAN_REVIEW.md). El plan inicial que sigue se conserva como antecedente. La detección solo propone defaults. Columnas estructuradas confirmadas usan sustitución completa sin NER y texto libre ofrece detección por entidades o reemplazo completo.

Gate inicial: PASS_WITH_NOTES, 20 de octubre de 2026. Prueba nativa real CPU Windows con Transformers 5.16.1/PyTorch 2.13.0 ya disponibles: carga e inferencia local exitosas, sin código remoto. Se verificará de nuevo en el entorno independiente fijado del proyecto antes de distribuir.

- Python version: 3.12.2, Windows x64. Distribución dirigida a Python 3.12.
- Presidio version: 2.2.364 (estable publicada en PyPI).
- Spanish NER model: OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1.
- Revisión inmutable: eb499b1b8349c606ca425b6d0f57777ae4ba79ff.
- Model license: Apache-2.0 según ficha del editor.
- Model size: 211.824.460 parámetros F32; aproximadamente 847 MB de pesos. Tamaño exacto en reports/model_probe.json tras descarga.
- CPU compatible: YES, probado en Windows. En primera frase sintética detecta teléfono pero omite nombre/correo; requiere evaluación independiente de NER y motor híbrido. No constituye garantía de recall adecuado.
- Estimated RAM: reservar inicialmente 4 GB para el proceso y 8 GB en el equipo. Es estimación de planificación, no benchmark.
- Faker locale: comprobar es_CR y proveedores; usar es_MX si no está disponible. Registrar decisión.
- Excel engine: openpyxl, edición de una copia cargada desde BytesIO.
- UI: Streamlit español, morado #663366, acentos #FF6633 y #009999, sin logo inventado.
- Detection strategy: headers normalizados + muestras distribuidas + recognizers Presidio CR + NER por lotes. Las columnas institucionales se protegen frente a etiquetas genéricas del NER; patrones inequívocos de correo/teléfono siguen generando alerta. ID genérico y nueve dígitos sin contexto no bastan.
- Replacement strategy: Faker español y valores explícitos de prueba; sustitución total de campos personales tipados y por spans en texto libre. Diccionario efímero compartido entre hojas, normalización Unicode/espacios. No repetir pseudónimos entre ejecuciones por requisito.
- Temporary-file strategy: uploads, workbook, mapping y descarga en memoria. Ninguna persistencia de entradas ni mappings. Borrar referencias al reiniciar; Python no garantiza borrado forense de RAM.
- Offline strategy: modelo íntegro local, local_files_only, sin trust_remote_code; telemetría desactivada, ningún modelo descargado durante uso. Probar bloqueo de sockets externos.
- Major risks: NER imperfecto; datos fuera de tablas/headers; fórmulas literales con PII; metadatos, comentarios, imágenes, vínculos y objetos embebidos; ZIP bombs; libros protegidos; fórmulas sin recálculo; consumo CPU. Rechazar características fuera del alcance en lugar de exportarlas silenciosamente.

## Fuentes primarias consultadas

- https://pypi.org/project/presidio-analyzer/ (versión y Python).
- https://microsoft.github.io/presidio/samples/ (integración mediante EntityRecognizer).
- https://huggingface.co/OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1 (licencia, ficha).
- https://huggingface.co/OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1/raw/eb499b1b8349c606ca425b6d0f57777ae4ba79ff/config.json (76 labels BIO/O y arquitectura).
- https://huggingface.co/docs/transformers/model_doc/eurobert (soporte nativo incorporado en 2026; la familia 4.57 no lo contiene).
- https://faker.readthedocs.io/en/master/locales.html (locales; prevalece prueba de instalación).
- https://docs.streamlit.io/develop/api-reference/configuration/config.toml (binding y telemetría).

Las métricas de la ficha del modelo no se usan como resultados propios. No se cambia de modelo. Se evaluará Transformers 5.20.2 para soporte nativo y evitar ejecutar los archivos Python remotos del repositorio del modelo.

## Resultado de la verificación

Entorno final independiente: Python 3.12.2, Presidio 2.2.364, Transformers 5.20.2, PyTorch 2.14.1, Streamlit 1.66.0, Faker 40.43.0, openpyxl 3.1.5. Inferencia local CPU sin código remoto: PASS. Pesos: 847.310.224 bytes. es_CR no existe en la lista de locales de Faker instalada; es_MX se probó con nombres y direcciones y se usa como alternativa explícita. La sonda registró aproximadamente 673 MiB de memoria residente del proceso; no equivale al máximo ni garantiza que 1 GB sea suficiente. Reservar margen de 4 GB para el proceso y 8 GB de RAM del equipo.

El conjunto sintético reveló recall insuficiente (ver reports/evaluation.json). Gate 2: FAIL. No se cambia silenciosamente de modelo ni se presentan las cifras publicadas por OpenMed como rendimiento propio. La herramienta queda etiquetada para evaluación con datos ficticios. Se revisó como candidato Piiranha multilingüe, pero su licencia actual CC-BY-NC-ND-4.0 y mayor tamaño requieren revisar distribución/uso antes de adoptarlo; no se descargó ni se integró, y no se afirma superioridad medida. Fuente: https://huggingface.co/iiiorg/piiranha-v1-detect-personal-information
