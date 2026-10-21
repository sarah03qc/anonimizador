"""Local launcher: explicit binding, readiness wait and browser open."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT=Path(__file__).resolve().parents[1]

def main():
    if not (ROOT/".installation_ok").exists():
        print("Esta herramienta todavía no está instalada. Ejecute primero setup_windows.ps1.")
        return 1
    # Refuse an occupied port instead of opening an unrelated local application.
    try:
        with socket.socket() as probe: probe.bind(("127.0.0.1",8501))
    except OSError:
        print("El puerto de la herramienta está ocupado. Cierre la otra instancia y vuelva a abrir.")
        return 1
    env=os.environ.copy()
    env.update(HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",HF_HUB_DISABLE_TELEMETRY="1",STREAMLIT_BROWSER_GATHER_USAGE_STATS="false",DO_NOT_TRACK="1")
    cmd=[sys.executable,"-m","streamlit","run",str(ROOT/"app.py"),"--server.address=127.0.0.1","--server.port=8501","--server.headless=true","--browser.gatherUsageStats=false"]
    process=subprocess.Popen(cmd,cwd=ROOT,env=env)
    local_http=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        for _ in range(180):
            if process.poll() is not None: return process.returncode or 1
            try:
                with local_http.open("http://127.0.0.1:8501/_stcore/health",timeout=1) as response:
                    if response.status==200:
                        opened=webbrowser.open("http://127.0.0.1:8501")
                        print("Navegador local solicitado: "+("correctamente" if opened else "abra http://127.0.0.1:8501"),flush=True)
                        break
            except OSError: time.sleep(.5)
        else:
            print("No fue posible iniciar la herramienta. Vuelva a ejecutar la instalación.")
            return 1
        print("Herramienta abierta. Mantenga esta ventana abierta. Para cerrar use Ctrl+C.",flush=True)
        return process.wait()
    except KeyboardInterrupt: return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill()

if __name__=="__main__": sys.exit(main())
