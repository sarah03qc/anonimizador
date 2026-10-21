import re
import unicodedata

def normalize(value):
    value = re.sub(r"([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])", r"\1 \2", str(value))
    value = ''.join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()

INSTITUTION = r"\b(region|oficina local|establecimiento|codigo ol|unidad institucional|departamento institucional|nombre de servicio|nombre servicio|tipo de servicio|tipo servicio)\b"
RULES = [
    (r"\b(fecha (de )?nacimiento|nacimiento|fec nac|f nac)\b", "Fecha personal"),
    (r"\b(correo|email|e mail)\b", "Correo"),
    (r"\b(telefono|tel|celular|movil|contacto)\b", "Teléfono"),
    (r"\b(cedula|identificacion|documento|id persona|identificador persona|dimex|pasaporte|expediente)\b", "Identificación"),
    (r"\b(cuenta bancaria|iban|tarjeta|cuenta banco)\b", "Financiero"),
    (r"\b(usuario|username|contrasena|password|clave|credencial)\b", "Credencial"),
    (r"\b(direccion|domicilio|residencia)\b", "Dirección / ubicación"),
    (r"\b(nombre|nombres|apellido|apellidos|madre|padre|encargado|responsable)\b", "Persona"),
    (r"\b(observacion|observaciones|nota|notas|comentario|comentarios)\b", "Texto con PII"),
]

def header_kind(header):
    h=normalize(header)
    if re.search(INSTITUTION,h): return "Institucional"
    for pattern,kind in RULES:
        if re.search(pattern,h): return kind
    return "No determinado"
