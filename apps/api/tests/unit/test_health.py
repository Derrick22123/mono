"""Unit tests for health status derivation."""

from app.health import derive_model_credentials, derive_overall_status


def test_derive_model_credentials_missing():
    assert derive_model_credentials(None) == "missing"
    assert derive_model_credentials("") == "missing"
    assert derive_model_credentials("   ") == "missing"


def test_derive_model_credentials_invalid():
    assert derive_model_credentials("bad-key") == "invalid"


def test_derive_model_credentials_ok():
    assert derive_model_credentials("sk-test123") == "ok"


def test_derive_overall_status_healthy():
    assert derive_overall_status(model_credentials="ok", model_reachable="ok") == "healthy"


def test_derive_overall_status_degraded_on_missing_credentials():
    assert (
        derive_overall_status(model_credentials="missing", model_reachable="skipped") == "degraded"
    )


def test_derive_overall_status_degraded_on_unreachable():
    assert derive_overall_status(model_credentials="ok", model_reachable="failed") == "degraded"
