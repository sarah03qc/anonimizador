import os
import sys

_installed = False

def offline_environment():
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_HUB_DISABLE_TELEMETRY="1", DO_NOT_TRACK="1", TOKENIZERS_PARALLELISM="false", STREAMLIT_BROWSER_GATHER_USAGE_STATS="false")

def block_external_network():
    """Audit hook cannot be removed by rerunning a Streamlit script."""
    global _installed
    offline_environment()
    if _installed: return
    def guard(event,args):
        if event in ("socket.connect", "socket.sendto"):
            address=args[1] if event=="socket.connect" else args[-1]
            if not isinstance(address,tuple) or address[0] not in ("127.0.0.1","::1","localhost"):
                raise PermissionError("Conexión externa deshabilitada durante el procesamiento local.")
        elif event=="socket.getaddrinfo" and args[0] not in (None,"127.0.0.1","::1","localhost"):
            raise PermissionError("Resolución externa deshabilitada.")
    sys.addaudithook(guard)
    _installed=True
