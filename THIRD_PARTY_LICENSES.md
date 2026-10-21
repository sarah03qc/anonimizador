# Componentes de terceros

La herramienta no adquiere carácter oficial por usar el nombre CEN-CINAI. No incluye logotipo. Revisar este inventario antes de redistribuir un paquete completo. Las licencias completas de las bibliotecas se conservan en `.venv/Lib/site-packages/*dist-info/licenses` o los archivos LICENSE del paquete. La ficha del modelo se conserva en `models/spanish-pii/README.md`.

- **Microsoft Presidio / presidio-analyzer** — MIT. Microsoft y colaboradores; mantenimiento actual data-privacy-stack. https://github.com/data-privacy-stack/presidio
- **OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1** — Apache License 2.0, según declaración del editor OpenMed. Revisión eb499b1b8349c606ca425b6d0f57777ae4ba79ff. Modelo base EuroBERT/EuroBERT-210m. https://huggingface.co/OpenMed/OpenMed-PII-Spanish-EuroMed-Large-210M-v1
- **EuroBERT** — Apache-2.0 según repositorio del modelo base. https://huggingface.co/EuroBERT/EuroBERT-210m
- **Transformers** — Apache-2.0, Hugging Face y colaboradores. https://github.com/huggingface/transformers
- **Hugging Face Hub / tokenizers / safetensors** — Apache-2.0. https://github.com/huggingface
- **PyTorch** — BSD de tres cláusulas; contiene avisos de componentes terceros propios. https://github.com/pytorch/pytorch/blob/main/LICENSE
- **Faker** — MIT, Joke2k y colaboradores. https://github.com/joke2k/faker
- **Streamlit** — Apache-2.0, Snowflake y colaboradores. https://github.com/streamlit/streamlit
- **openpyxl** — MIT. https://openpyxl.readthedocs.io/
- **spaCy** — MIT, Explosion y colaboradores. Dependencia de Presidio; no se descarga modelo spaCy adicional. https://github.com/explosion/spaCy
- **defusedxml** — PSF. https://github.com/tiran/defusedxml
- **psutil** — BSD de tres cláusulas. https://github.com/giampaolo/psutil
- **pytest** — MIT. https://github.com/pytest-dev/pytest
- **pip-audit** — Apache-2.0. https://github.com/pypa/pip-audit
- **NumPy / pandas / SciPy si aparece como transitiva** — BSD de tres cláusulas; consultar avisos en distribución.
- **Apache Arrow / pyarrow, Altair, pydeck** — Apache-2.0 o BSD según paquete; ver inventario generado de licencias.

No se ejecutan los archivos Python personalizados del repositorio OpenMed. Se utilizan los pesos safetensors con la implementación nativa de Transformers. No se altera el modelo ni se atribuyen a esta herramienta las métricas publicadas por OpenMed.

Las pruebas sintéticas no utilizan registros ni beneficiarios reales. Los nombres comunes generados pueden coincidir por azar con personas existentes y no deben utilizarse como identidades.

Se incluye el texto íntegro de Apache License 2.0 en `licenses/APACHE-2.0.txt`. El inventario de las 118 distribuciones instaladas y las rutas de sus avisos/licencias está en `reports/dependency_licenses.json`. Al redistribuir una instalación completa, conserve esos avisos y la ficha del modelo. El modelo se distribuye sin modificaciones a sus pesos; la capa de detección y el mapeo de etiquetas pertenecen a la aplicación.
