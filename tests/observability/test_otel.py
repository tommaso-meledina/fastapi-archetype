from __future__ import annotations

import logging

from fastapi_archetype.core.config import AppSettings
from fastapi_archetype.observability import otel


def test_setup_otel_with_export_disabled_logs_and_sets_provider(
    monkeypatch,
    caplog,
) -> None:
    settings = AppSettings(otel_export_enabled=False)
    captured: dict[str, object] = {}

    def fake_set_tracer_provider(provider):  # noqa: ANN001
        captured["provider"] = provider

    monkeypatch.setattr(otel.trace, "set_tracer_provider", fake_set_tracer_provider)

    with caplog.at_level(logging.INFO):
        provider = otel.setup_otel(settings)

    assert captured["provider"] is provider
    assert "OTEL trace export disabled" in caplog.text
