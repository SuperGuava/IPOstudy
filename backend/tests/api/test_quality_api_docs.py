from pathlib import Path


def test_quality_endpoints_documented() -> None:
    root = Path(__file__).resolve().parents[3]
    openapi = (root / "docs" / "openapi.yaml").read_text(encoding="utf-8")
    assert "/quality/issues:" in openapi
    assert "/quality/summary:" in openapi
    assert "/quality/entity/{entity_key}:" in openapi
