from __future__ import annotations

import logging

from fastapi import FastAPI

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.observability import otel


def test_setup_otel_with_export_disabled_logs_and_instruments(
    monkeypatch,
    caplog,
) -> None:
    app = FastAPI()
    settings = AppSettings(otel_export_enabled=False)
    instrumented: dict[str, object] = {}

    def fake_set_tracer_provider(provider):  # noqa: ANN001
        instrumented["provider"] = provider

    def fake_instrument_app(fastapi_app, excluded_urls):  # noqa: ANN001
        instrumented["app"] = fastapi_app
        instrumented["excluded_urls"] = excluded_urls

    monkeypatch.setattr(otel.trace, "set_tracer_provider", fake_set_tracer_provider)
    monkeypatch.setattr(
        otel.FastAPIInstrumentor,
        "instrument_app",
        staticmethod(fake_instrument_app),
    )

    with caplog.at_level(logging.INFO):
        provider = otel.setup_otel(app, settings)

    assert instrumented["provider"] is provider
    assert instrumented["app"] is app
    assert instrumented["excluded_urls"] == "metrics"
    assert "OTEL trace export disabled" in caplog.text
