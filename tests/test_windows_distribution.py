"""Packaging-only checks. Does not alter the 108 functional regression tests."""
import ctypes
from ctypes import wintypes
import importlib.util
from pathlib import Path
import socket,subprocess,sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('distribution_launcher',ROOT/'windows/launcher.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)

def test_frozen_resources_are_relative_to_bundle(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'_MEIPASS',str(tmp_path),raising=False)
    assert launcher.root_path()==tmp_path.resolve()

def test_missing_bundle_components_fail_closed(tmp_path):
    with pytest.raises(RuntimeError,match='resources'):launcher.check_resources(tmp_path)

def test_free_port_skips_occupied_loopback_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1',0));s.listen();occupied=s.getsockname()[1]
        if occupied>65430:pytest.skip('No room for probe range')
        chosen=launcher.free_port(occupied)
        assert chosen!=occupied
        with socket.socket() as check:check.bind(('127.0.0.1',chosen))

@pytest.mark.skipif(sys.platform!='win32',reason='Windows job lifecycle')
def test_job_closes_associated_process():
    process=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],creationflags=subprocess.CREATE_NO_WINDOW)
    job=launcher.WindowsJob()
    try:
        job.assign(process);job.close()
        process.wait(timeout=10)
        assert process.poll() is not None
    finally:
        job.close()
        if process.poll() is None:process.kill();process.wait()

@pytest.mark.skipif(sys.platform!='win32',reason='Windows single-instance mutex')
def test_mutex_prevents_second_launcher(monkeypatch):
    monkeypatch.setattr(launcher,'message',lambda text:None)
    first=launcher.mutex()
    assert first is not None
    try:assert launcher.mutex() is None
    finally:ctypes.windll.kernel32.CloseHandle(wintypes.HANDLE(first))

def test_payload_does_not_collect_project_or_candidate_directories():
    spec_source=(ROOT/'windows/Anonimizador.spec').read_text()
    assert "root/'models/spanish-pii'" in spec_source
    assert "root/'models'" not in spec_source
    assert "root/'test_data'" not in spec_source
    assert "root/'reports'" not in spec_source
    assert 'console=False' in spec_source and "contents_directory='_internal'" in spec_source
