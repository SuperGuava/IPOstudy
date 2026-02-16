from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.connectors.krx_connector import KrxAuthError, KrxConnector


def load_env_from_repo_root() -> dict[str, str]:
    env: dict[str, str] = {}
    root_env = Path(__file__).resolve().parents[2] / ".env"
    if not root_env.exists():
        return env
    for line in root_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def resolve_krx_stock_path(env: dict[str, str]) -> str:
    return env.get("KRX_API_STOCK_PATH", "sto/stk_isu_base_info")


def _split_paths(raw: str) -> list[str]:
    return [path.strip() for path in raw.split(",") if path.strip()]


def resolve_probe_paths(env: dict[str, str]) -> dict[str, list[str]]:
    return {
        "index": _split_paths(env.get("KRX_API_INDEX_PATH", "")),
        "stock": _split_paths(resolve_krx_stock_path(env)),
        "securities": _split_paths(env.get("KRX_API_SECURITIES_PATH", "")),
        "bond": _split_paths(env.get("KRX_API_BOND_PATH", "")),
        "derivative": _split_paths(env.get("KRX_API_DERIVATIVE_PATH", "")),
        "general": _split_paths(env.get("KRX_API_GENERAL_PATH", "")),
        "esg": _split_paths(env.get("KRX_API_ESG_PATH", "")),
    }


def main() -> int:
    env = load_env_from_repo_root()
    api_key = env.get("KRX_API_KEY")
    probe_paths = resolve_probe_paths(env)
    if not api_key:
        print("KRX_API_KEY is missing in .env")
        return 2

    connector = KrxConnector(api_key=api_key)
    stock_status = "not_checked"
    had_other_error = False
    for category, api_paths in probe_paths.items():
        if not api_paths:
            print(f"KRX Open API SKIP: category={category} path=not_configured")
            continue
        category_has_success = False
        category_had_auth = False
        category_had_error = False
        for api_path in api_paths:
            try:
                payload = connector.fetch_open_api(api_path, {"basDd": "20250131"})
                rows = payload.get("OutBlock_1", []) if isinstance(payload, dict) else []
                print(f"KRX Open API OK: category={category} path={api_path} rows={len(rows)}")
                category_has_success = True
            except KrxAuthError as exc:
                print(f"KRX Open API AUTH ERROR: category={category} path={api_path} error={exc}")
                category_had_auth = True
            except Exception as exc:  # pragma: no cover - diagnostic script path
                print(f"KRX Open API ERROR: category={category} path={api_path} error={type(exc).__name__}: {exc}")
                category_had_error = True
                had_other_error = True

        if category == "stock":
            if category_has_success:
                stock_status = "ok"
            elif category_had_auth:
                stock_status = "auth_error"
            elif category_had_error:
                stock_status = "error"

    if stock_status == "ok":
        return 0
    if stock_status == "auth_error":
        print("Check API key issuance and API usage approval in KRX Open API portal.")
        return 3
    if stock_status in {"not_checked", "error"} or had_other_error:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
