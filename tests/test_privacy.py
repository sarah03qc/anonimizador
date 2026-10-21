from pathlib import Path
import subprocess
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[1]

def test_T33_localhost_config():
    config=tomllib.loads((ROOT/".streamlit/config.toml").read_text())
    assert config["server"]["address"]=="127.0.0.1"
    assert config["browser"]["gatherUsageStats"] is False
    assert "--server.address=127.0.0.1" in (ROOT/"scripts/launch.py").read_text()

def test_T34_real_model_offline():
    result=subprocess.run([sys.executable,str(ROOT/"scripts/smoke_check.py")],cwd=ROOT,capture_output=True,text=True,timeout=240)
    assert result.returncode==0, result.stderr[-2000:]

def test_external_socket_blocked():
    script="from anonymizer.privacy import block_external_network; block_external_network(); import socket; socket.create_connection(('192.0.2.1',80),timeout=.1)"
    result=subprocess.run([sys.executable,"-c",script],cwd=ROOT,capture_output=True,text=True,timeout=20)
    assert result.returncode!=0
    assert "PermissionError" in result.stderr
