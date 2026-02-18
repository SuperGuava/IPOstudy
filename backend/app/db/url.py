from __future__ import annotations


def normalize_database_url(raw_url: str | None, *, default: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return default
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url

