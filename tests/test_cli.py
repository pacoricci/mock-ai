import types
from pathlib import Path

from typer.testing import CliRunner

import mock_ai.__main__ as main
from mock_ai.settings import UvicornSettings, uvicorn_settings


def reset_settings() -> None:
    """Reset uvicorn settings to defaults."""
    defaults = UvicornSettings()
    for name in defaults.model_fields:
        setattr(uvicorn_settings, name, getattr(defaults, name))


def test_dev_command_overrides_settings(monkeypatch):
    reset_settings()
    called: dict[str, object] = {}

    def fake_run(*_args, **kwargs):
        called.update(kwargs)

    monkeypatch.setattr(main.uvicorn, "run", fake_run)
    runner = CliRunner()
    result = runner.invoke(
        main.app,
        [
            "dev",
            "--host",
            "1.1.1.1",
            "--port",
            "1234",
            "--reload",
            "False",
            "--root-path",
            "/x",
            "--proxy-headers",
            "False",
            "--timeout-keep-alive",
            "11",
            "--ssl-certfile",
            "cert.pem",
            "--ssl-keyfile",
            "key.pem",
            "--ssl-keyfile-password",
            "pass",
        ],
    )
    assert result.exit_code == 0
    assert uvicorn_settings.host == "1.1.1.1"
    assert uvicorn_settings.port == 1234
    assert uvicorn_settings.reload is False
    assert uvicorn_settings.root_path == "/x"
    assert uvicorn_settings.proxy_headers is False
    assert uvicorn_settings.timeout_keep_alive == 11
    assert uvicorn_settings.ssl_certfile == Path("cert.pem")
    assert uvicorn_settings.ssl_keyfile == Path("key.pem")
    assert uvicorn_settings.ssl_keyfile_password == "pass"

    expected = {
        "app": "mock_ai.app:app",
        "host": "1.1.1.1",
        "port": 1234,
        "reload": False,
        "workers": uvicorn_settings.workers,
        "root_path": "/x",
        "proxy_headers": False,
        "timeout_keep_alive": 11,
        "ssl_certfile": Path("cert.pem"),
        "ssl_keyfile": Path("key.pem"),
        "ssl_keyfile_password": "pass",
    }
    assert called == expected
    reset_settings()


def test_run_command_overrides_settings(monkeypatch):
    reset_settings()
    called: dict[str, object] = {}

    def fake_run(*_args, **kwargs):
        called.update(kwargs)

    monkeypatch.setattr(main.uvicorn, "run", fake_run)
    runner = CliRunner()
    result = runner.invoke(
        main.app,
        [
            "run",
            "--host",
            "2.2.2.2",
            "--port",
            "9876",
            "--reload",
            "False",
            "--workers",
            "3",
            "--root-path",
            "/prod",
            "--proxy-headers",
            "True",
            "--timeout-keep-alive",
            "22",
            "--ssl-certfile",
            "cert2.pem",
            "--ssl-keyfile",
            "key2.pem",
            "--ssl-keyfile-password",
            "pass2",
        ],
    )
    assert result.exit_code == 0
    assert uvicorn_settings.host == "2.2.2.2"
    assert uvicorn_settings.port == 9876
    assert uvicorn_settings.reload is False
    assert uvicorn_settings.workers == 3
    assert uvicorn_settings.root_path == "/prod"
    assert uvicorn_settings.proxy_headers is True
    assert uvicorn_settings.timeout_keep_alive == 22
    assert uvicorn_settings.ssl_certfile == Path("cert2.pem")
    assert uvicorn_settings.ssl_keyfile == Path("key2.pem")
    assert uvicorn_settings.ssl_keyfile_password == "pass2"

    expected = {
        "app": "mock_ai.app:app",
        "host": "2.2.2.2",
        "port": 9876,
        "reload": False,
        "workers": 3,
        "root_path": "/prod",
        "proxy_headers": True,
        "timeout_keep_alive": 22,
        "ssl_certfile": Path("cert2.pem"),
        "ssl_keyfile": Path("key2.pem"),
        "ssl_keyfile_password": "pass2",
    }
    assert called == expected
    reset_settings()
