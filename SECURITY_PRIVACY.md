# Seguridad y privacidad

La revisión de controles de privacidad no equivale a aprobación de la detección. La calidad del detector de entidades sigue siendo insuficiente. La revisión humana obligatoria controla las decisiones por columna: la UI exige confirmación y las columnas estructuradas confirmadas se sustituyen sin NER. El texto libre requiere advertencia o reemplazo completo. Un piloto real solo procede con autorización y validación supervisada, sin considerar la copia automáticamente apta para difusión.

## Alcance

Herramienta independiente de uso local para personal autorizado. No se conecta a SIA-CENCINAI, SIDINACC, bases institucionales ni servicios de inferencia. La instalación descarga bibliotecas y el modelo público; el procesamiento de archivos usa exclusivamente recursos locales.

El servidor escucha solo en **127.0.0.1**. La telemetría de Streamlit y Hugging Face se desactiva. El punto de entrada instala una barrera de sockets que rechaza conexiones salientes fuera del loopback. La barrera cubre Python y no sustituye las políticas del equipo, antivirus, extensiones del navegador o sincronización de carpetas.

## Datos en memoria

El archivo cargado, las muestras, la copia y el diccionario original→sintético se mantienen en memoria. No se usan archivos temporales de entrada/salida, bases de datos ni cachés de datos en disco. El modelo puede compartirse como recurso sin contenido de celdas. El diccionario de pseudónimos y la caché de detección se vacían en `finally`, incluso si hay errores. Se pueden conservar la entrada y la descarga en la sesión mientras la usuaria revisa o descarga. **Procesar otro archivo** limpia esas referencias.

Las decisiones de revisión contienen encabezados, coordenadas, categorías y métodos, sin valores de celdas. Permanecen en la sesión y no se guardan como perfil ni se registran. La confirmación usa un SHA-256 del libro y exige todas las columnas, también las ocultas. Editar una decisión, reaplicar un perfil, reanalizar, cambiar encabezados o archivo invalida la confirmación y la salida. Los perfiles distribuidos son estáticos y ficticios; YAML se carga con `safe_load`, sin ejecutar código.

Python no garantiza el borrado físico inmediato de todas las copias en RAM. El sistema operativo puede usar paginación o volcados de memoria. Una descarga decidida por la usuaria se guarda mediante el navegador y queda bajo las políticas del equipo. La carpeta actual está en OneDrive: no debe colocarse allí información personal ni asumirse que los archivos descargados fuera de la aplicación quedan excluidos de sincronización.

## Registro y errores

No se registran celdas, pseudovalores, nombres de archivos del usuario ni parejas de valores. Los errores se presentan con mensajes fijos; no se muestra el texto de excepciones ni trazas. Las pruebas y benchmarks solo usan datos ficticios. Los reportes contienen cantidades, tiempos, versiones y métricas, nunca mappings ni uploads.

## Excel y revisión humana

Se rechazan libros cifrados/protegidos y características no cubiertas que puedan conservar datos ocultos: macros, vínculos externos, comentarios, objetos, imágenes, tablas dinámicas, conexiones y similares. Se examinan hojas ocultas, filas y columnas ocultas. Las propiedades descriptivas del documento se limpian al generar la copia. Los nombres de hojas y encabezados se conservan: la persona revisora debe comprobar que no contienen datos personales.

Las fórmulas se conservan cuando son compatibles. Se rechazan fórmulas con literales de texto o referencias externas para evitar conservar PII incrustada. No se evalúan ni se ejecutan fórmulas. No se garantiza que las combinaciones de variables indirectas (edad, región, servicio) impidan reidentificación.

Los identificadores de salida incluyen un prefijo de prueba; los correos usan `example.test` y los teléfonos un prefijo no operativo. No se afirma validez de registros oficiales. Esta herramienta realiza sustitución sintética/pseudonimización; su resultado necesita validación humana y no equivale por sí solo a una anonimización irreversible.

## Validación

Consultar `reports/` para pruebas de bloqueo de red, conservación del libro, evaluación sintética y revisión independiente. Los resultados pendientes o fallidos se identifican explícitamente en el informe final. No utilizar registros reales hasta completar el piloto autorizado.
