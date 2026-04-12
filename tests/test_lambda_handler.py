import asyncio

from mangum import Mangum

import lambda_handler
from main import app


def test_lambda_asgi_handler_wraps_server_app():
    assert isinstance(lambda_handler.asgi_handler, Mangum)
    assert lambda_handler.asgi_handler.app is app
    assert lambda_handler.asgi_handler.lifespan == "auto"


def test_handler_runs_migrations_once_before_asgi_handler(monkeypatch):
    calls = []

    def fake_upgrade(config, revision):
        calls.append(("upgrade", config.config_file_name, revision))

    def fake_asgi_handler(event, context):
        calls.append(("asgi", event, context))
        return {"statusCode": 200}

    monkeypatch.setattr(lambda_handler, "_migrations_ran", False)
    monkeypatch.setattr(lambda_handler.command, "upgrade", fake_upgrade)
    monkeypatch.setattr(lambda_handler, "asgi_handler", fake_asgi_handler)

    first_event = {"request": 1}
    second_event = {"request": 2}
    context = object()

    assert lambda_handler.handler(first_event, context) == {"statusCode": 200}
    assert lambda_handler.handler(second_event, context) == {"statusCode": 200}

    assert calls == [
        ("upgrade", str(lambda_handler._alembic_config_path), "head"),
        ("asgi", first_event, context),
        ("asgi", second_event, context),
    ]


def test_handler_restores_event_loop_after_async_migration(monkeypatch):
    async def async_migration():
        return None

    def fake_upgrade(config, revision):
        asyncio.run(async_migration())

    def fake_asgi_handler(event, context):
        assert asyncio.get_event_loop() is not None
        return {"statusCode": 200}

    monkeypatch.setattr(lambda_handler, "_migrations_ran", False)
    monkeypatch.setattr(lambda_handler.command, "upgrade", fake_upgrade)
    monkeypatch.setattr(lambda_handler, "asgi_handler", fake_asgi_handler)

    assert lambda_handler.handler({}, object()) == {"statusCode": 200}
