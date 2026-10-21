# Anonimizador CEN-CINAI

**Herramienta de detección asistida y anonimización con revisión humana.** Las selecciones automáticas son una ayuda: revise todas las columnas. Para un piloto con datos reales, solicite autorización y validación supervisada; la copia no queda aprobada automáticamente para difusión.

## Primera vez

Reciba el ZIP portable de Windows y extraiga la carpeta completa en una ubicación autorizada. Abra **Anonimizador CEN-CINAI.exe**. No necesita instalar Python, abrir una terminal ni ejecutar comandos. Mantenga todos los archivos juntos, incluida la carpeta `_internal`. Las instrucciones de `setup_windows.ps1` corresponden únicamente al entorno de desarrollo de informática.

## Cada vez que lo use

1. Haga doble clic en **Anonimizador CEN-CINAI.exe**. Aparecerá una ventana de inicio y se abrirá el navegador. Espere; la primera carga del modelo puede tardar.
2. Seleccione o arrastre un archivo **.xlsx**. No se acepta .xls ni .xlsm.
3. Espere el análisis. El archivo se procesa únicamente en este equipo y no se envía a Internet.
4. Revise **todas las hojas**, incluidas las ocultas. Confirme la fila de encabezados de cada hoja. Si su libro no tiene una tabla por hoja, solicite ayuda para prepararlo.
5. Revise todas las columnas de todas las hojas. Marque las que desea sustituir y desmarque recomendaciones incorrectas. Puede cambiar tipo y método en la tabla o en **Ajustar una columna con controles**. Los estados son 🔴 **Sensible**, 🟡 **Revisar**, 🟢 **Sin indicadores detectados** y 🔵 **Institucional**. Ninguno sustituye su revisión.
6. En cada amarilla, elija explícitamente **Anonimizar** o **Conservar**. Para personas, identificaciones, teléfonos, correos, direcciones, fechas personales, credenciales y datos financieros, se sustituyen todos los valores literales no vacíos. Para **Texto libre**, elija **Detectar y sustituir entidades** (puede omitir información) o **Reemplazar contenido completo** (elimina toda la nota y deja `[CONTENIDO ANONIMIZADO]`).
7. Marque **He revisado todas las columnas y confirmé cuáles deben anonimizarse**, pulse **CONFIRMAR SELECCIÓN**, compruebe el resumen y presione **ANONIMIZAR ARCHIVO**. Si modifica una decisión, deberá confirmar nuevamente; la copia anterior se descarta.
8. Presione **DESCARGAR ARCHIVO ANONIMIZADO**. El nombre termina en **_anonimizado.xlsx**. Se guarda donde su navegador indique. El original no se modifica.
9. Abra la copia con Excel y revísela antes de compartirla fuera del entorno autorizado. Excel podrá recalcular las fórmulas al abrirla.
10. Use **Procesar otro archivo** para limpiar la sesión. Al terminar, pulse **Cerrar herramienta** en la ventana de inicio. Cerrar solo la pestaña del navegador no apaga el servidor. Si cerró la pestaña por error, pulse **Abrir aplicación** en esa ventana.

## Si aparece un error

- **Carpeta incompleta:** vuelva a extraer el ZIP completo; no copie solamente el ejecutable.
- **Archivo no válido:** confirme que puede abrirlo en Excel y que es .xlsx.
- **Características no admitidas:** prepare una copia de solo tablas, sin comentarios, vínculos, objetos o contenido externo. Conserve siempre su original.
- **Libro protegido:** solicite una copia autorizada sin protección. La herramienta no quita contraseñas.
- **Límite excedido:** divida una copia del libro y procese cada parte.

La detección dentro de texto libre puede no identificar toda la información sensible. Si tiene dudas, utilice el reemplazo completo. Revise también encabezados, nombres de hojas, fórmulas conservadas y combinaciones de datos que permitan reidentificación. Los teléfonos e identificadores generados son datos sintéticos y no corresponden a personas reales; no se afirma validez oficial.
