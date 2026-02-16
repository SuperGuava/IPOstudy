import argparse
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


def parse_strict_categories(raw: str) -> list[str]:
    return [value.strip() for value in raw.split(",") if value.strip()]


def category_has_success(details: list[dict]) -> bool:
    return any(detail.get("status") == "ok" for detail in details)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe KRX Open API configured category paths.")
    parser.add_argument("--bas-dd", default="20250131", help="KRX basDd (YYYYMMDD)")
    parser.add_argument("--repeat", type=int, default=1, help="Probe repeat count")
    parser.add_argument(
        "--strict-categories",
        default="stock",
        help="Comma-separated categories that must have at least one OK path",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    env = load_env_from_repo_root()
    api_key = env.get("KRX_API_KEY")
    probe_paths = resolve_probe_paths(env)
    if not api_key:
        print("KRX_API_KEY is missing in .env")
        return 2

    connector = KrxConnector(api_key=api_key)
    strict_categories = parse_strict_categories(args.strict_categories)
    category_results: dict[str, list[dict]] = {category: [] for category in probe_paths.keys()}
    had_other_error = False
    repeat_count = max(1, args.repeat)
    for turn in range(1, repeat_count + 1):
        if repeat_count > 1:
            print(f"--- probe iteration {turn}/{repeat_count} ---")
        for category, api_paths in probe_paths.items():
            if not api_paths:
                print(f"KRX Open API SKIP: category={category} path=not_configured")
                category_results[category].append({"path": "not_configured", "status": "skip", "rows": 0})
                continue
            for api_path in api_paths:
                try:
                    payload = connector.fetch_open_api(api_path, {"basDd": args.bas_dd})
                    rows = payload.get("OutBlock_1", []) if isinstance(payload, dict) else []
                    print(f"KRX Open API OK: category={category} path={api_path} rows={len(rows)}")
                    category_results[category].append({"path": api_path, "status": "ok", "rows": len(rows)})
                except KrxAuthError as exc:
                    print(f"KRX Open API AUTH ERROR: category={category} path={api_path} error={exc}")
                    category_results[category].append(
                        {"path": api_path, "status": "auth_error", "rows": 0, "error": str(exc)}
                    )
                except Exception as exc:  # pragma: no cover - diagnostic script path
                    print(
                        f"KRX Open API ERROR: category={category} path={api_path} error={type(exc).__name__}: {exc}"
                    )
                    category_results[category].append(
                        {"path": api_path, "status": "error", "rows": 0, "error": f"{type(exc).__name__}: {exc}"}
                    )
                    had_other_error = True

    failed_strict_categories: list[str] = []
    for category in strict_categories:
        details = category_results.get(category, [])
        if not category_has_success(details):
            failed_strict_categories.append(category)

    if not failed_strict_categories and not had_other_error:
        return 0
    if failed_strict_categories:
        print(f"Strict category check failed: {', '.join(failed_strict_categories)}")
        print("Check API key issuance and API usage approval in KRX Open API portal.")
        return 3
    if had_other_error:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
