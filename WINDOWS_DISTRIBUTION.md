# Distribución Windows

La aplicación funcional y el modelo no se modifican. Se utiliza PyInstaller **6.22.3**, hooks **2026.9**, modo **onedir / windowed**. El usuario final recibe una carpeta completa con el ejecutable, Python y bibliotecas privados, recursos de Streamlit y los pesos/tokenizer locales de OpenMed. No necesita instalar Python, pip, un entorno virtual ni ejecutar comandos.

## Fuente y artefactos

El repositorio contiene código, tests, documentación, `windows/Anonimizador.spec`, el launcher y los scripts de build. `models/`, `.venv/`, `build/`, `dist/`, `release/`, reportes y cachés están excluidos de Git. El ZIP y el instalador pertenecen a una entrega/release de GitHub, no al historial normal de código. No se crea repositorio remoto, commit ni push automáticamente.

El modelo para desarrollo se descarga con `setup_windows.ps1` o con el instalador de modelo del proyecto, después de preparar el entorno y sus dependencias. Se mantiene la revisión `eb499b1b8349c606ca425b6d0f57777ae4ba79ff`; la integridad se compara con `model_manifest.json`. No descargar ni añadir los candidatos de QA para construir esta entrega.

## Requisitos de build para informática

Windows x64 y Python 3.12, entorno del proyecto preparado según README, modelo local completo y espacio para el entorno, build, distribución, ZIP y copias de validación. Instale las versiones de `requirements-build.txt` en el entorno de build. La instalación inicial de dependencias/modelo requiere Internet; el ejecutable distribuido no.

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\scripts\build_windows.ps1
```

El script limpia únicamente las rutas de build/distribución generadas tras comprobar que pertenecen al proyecto, prepara el icono y avisos de terceros, ejecuta el `.spec`, retira fixtures de test que algunos hooks de dependencias copian como datos, valida archivos y huellas del modelo y crea el ZIP completo. Las APIs internas de bibliotecas como `torch.testing` forman parte de su código de soporte y no son datasets del proyecto. `-SkipZip` permite validar primero el bundle. La versión del intérprete, bibliotecas y hooks debe coincidir con los archivos fijados. La reproducibilidad es funcional y de recursos; no se promete ZIP o EXE idéntico bit a bit entre máquinas/fechas.

## Launcher y recursos

`windows/launcher.py` resuelve recursos desde `sys._MEIPASS`. `app.py`, perfiles y configuración se ubican dentro de `_internal`; la ruta existente del NER resuelve `_internal/models/spanish-pii`, sin cambio funcional. El puerto libre se busca desde 8501 y el servidor escucha exclusivamente en 127.0.0.1. Las conexiones externas Python quedan bloqueadas antes de iniciar Streamlit y se fuerza modo offline sin caché externo del modelo.

El ejecutable abre una ventana de estado y un servidor hijo del mismo ejecutable. No usa `python.exe`, `.venv`, comandos del sistema ni una consola visible. Un mutex de Windows evita el doble inicio y restaura la ventana existente. Un Job Object con `KILL_ON_JOB_CLOSE` liga la vida del servidor al launcher, incluso si el proceso padre termina de forma forzada. **Cerrar herramienta** y la X de la ventana de inicio cierran el servidor asociado.

Cerrar solo una pestaña del navegador no detiene el servidor: detectar el cierre de pestañas de forma fiable no es una capacidad estable de Streamlit. La ventana de inicio permanece abierta para reabrir el navegador o terminar la herramienta. No hay archivos de estado ni uploads persistentes en el uso normal. Los flags de diagnóstico `--qa-status` y `--diagnostics-log` son exclusivos de validación, nunca accesos directos para usuarios ni registro de datos reales.

## Validación obligatoria de entrega

1. Verifique hashes del modelo, subsistema GUI del EXE y exclusión de assets de desarrollo con `scripts/validate_windows_bundle.py`.
2. Copie exclusivamente la carpeta de `dist` a una carpeta temporal limpia fuera del proyecto, con espacios en el nombre. Ejecute su EXE con PATH limitado a Windows, sin PYTHONPATH/PYTHONHOME ni caché Hugging Face externo. El reporte de startup QA debe apuntar únicamente a esa copia y su Python privado.
3. Complete el E2E real desde ese ejecutable: carga XLSX ficticio, análisis con modelo local, revisión humana, confirmación, anonimización y descarga. Verifique el original por SHA-256 y la copia con openpyxl. Nunca usar datos reales en QA.
4. Mantenga activo el bloqueo de conexiones externas durante toda la ejecución. Revise la vinculación loopback y que no aparezcan dependencias de rutas de desarrollo.
5. Cree el ZIP con `scripts/zip_windows_bundle.py`, valide CRC y SHA-256, extráigalo a otra carpeta limpia y repita el smoke E2E desde ese EXE.
6. Solo después considere un instalador por usuario; la calidad del portable es independiente.

Los pasos de copia limpia, retirada de rutas de Python, diagnóstico real del modelo y apertura del EXE pueden repetirse mediante `scripts/test_windows_portable.ps1`; agregue `-FromZip` para extraer a otra carpeta temporal. El diagnóstico usa únicamente el Python privado del EXE. El E2E de navegador y la verificación del XLSX descargado se documentan por separado. `scripts/check_source_release.py` comprueba exclusiones de Git, binarios grandes y conservación de la app y sus tests previos.

## Distribución a Alina

Entregue el ZIP portable completo. Alina lo extrae, abre **Anonimizador CEN-CINAI.exe**, espera el navegador y sigue `LEAME.txt`. No debe separar el EXE de `_internal` ni ejecutar sin extraer. Use una ubicación autorizada, con controles de sincronización y descargas adecuados. El icono es geométrico y genérico; no utiliza el logotipo institucional.

El paquete no está firmado digitalmente. La validación local no equivale a certificación en otro equipo ni evita controles de seguridad de Windows. Se recomienda una prueba final en un Windows x64 autorizado sin Python, con memoria suficiente, antes de distribución amplia. No se necesita GPU. La primera carga del modelo puede tardar y el bundle es grande por PyTorch y los pesos.

Fuentes técnicas primarias: [runtime de PyInstaller](https://pyinstaller.org/en/stable/runtime-information.html), [opciones de empaquetado](https://www.pyinstaller.org/en/stable/usage.html), [hooks](https://www.pyinstaller.org/en/stable/hooks.html), [Job Objects de Windows](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
