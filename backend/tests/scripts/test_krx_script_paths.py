from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_script_module(name: str):
    script_path = Path(__file__).resolve().parents[2] / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, script_path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_pipeline_once = _load_script_module("run_pipeline_once")
krx_openapi_probe = _load_script_module("krx_openapi_probe")


def test_run_pipeline_once_uses_env_stock_path() -> None:
    env = {"KRX_API_STOCK_PATH": "sto/stk_bydd_trd"}
    assert run_pipeline_once.resolve_krx_stock_path(env) == "sto/stk_bydd_trd"


def test_run_pipeline_once_stock_path_falls_back_to_default() -> None:
    assert run_pipeline_once.resolve_krx_stock_path({}) == "sto/stk_isu_base_info"


def test_probe_uses_env_stock_path() -> None:
    env = {"KRX_API_STOCK_PATH": "sto/stk_bydd_trd"}
    assert krx_openapi_probe.resolve_krx_stock_path(env) == "sto/stk_bydd_trd"


def test_probe_stock_path_falls_back_to_default() -> None:
    assert krx_openapi_probe.resolve_krx_stock_path({}) == "sto/stk_isu_base_info"


def test_probe_resolves_all_category_paths() -> None:
    env = {
        "KRX_API_INDEX_PATH": "idx/krx_dd_trd",
        "KRX_API_STOCK_PATH": "sto/stk_bydd_trd",
        "KRX_API_SECURITIES_PATH": "sto/ksq_bydd_trd",
        "KRX_API_BOND_PATH": "bon/bnd_bydd_trd",
        "KRX_API_DERIVATIVE_PATH": "drv/opt_bydd_trd",
        "KRX_API_GENERAL_PATH": "gen/some_path",
        "KRX_API_ESG_PATH": "esg/some_path",
    }
    assert krx_openapi_probe.resolve_probe_paths(env) == {
        "index": ["idx/krx_dd_trd"],
        "stock": ["sto/stk_bydd_trd"],
        "securities": ["sto/ksq_bydd_trd"],
        "bond": ["bon/bnd_bydd_trd"],
        "derivative": ["drv/opt_bydd_trd"],
        "general": ["gen/some_path"],
        "esg": ["esg/some_path"],
    }


def test_probe_resolves_defaults_for_missing_optional_categories() -> None:
    assert krx_openapi_probe.resolve_probe_paths({}) == {
        "index": [],
        "stock": ["sto/stk_isu_base_info"],
        "securities": [],
        "bond": [],
        "derivative": [],
        "general": [],
        "esg": [],
    }


def test_probe_splits_comma_separated_paths() -> None:
    env = {
        "KRX_API_INDEX_PATH": "idx/krx_dd_trd, idx/kospi_dd_trd, idx/kosdaq_dd_trd",
    }
    paths = krx_openapi_probe.resolve_probe_paths(env)
    assert paths["index"] == ["idx/krx_dd_trd", "idx/kospi_dd_trd", "idx/kosdaq_dd_trd"]


def test_probe_parse_strict_categories() -> None:
    assert krx_openapi_probe.parse_strict_categories("stock, esg ,bond") == ["stock", "esg", "bond"]
    assert krx_openapi_probe.parse_strict_categories("  ") == []


def test_probe_category_success_when_any_path_is_ok() -> None:
    details = [
        {"path": "a", "status": "auth_error"},
        {"path": "b", "status": "ok"},
    ]
    assert krx_openapi_probe.category_has_success(details) is True


def test_probe_category_success_false_when_all_failed() -> None:
    details = [
        {"path": "a", "status": "auth_error"},
        {"path": "b", "status": "error"},
    ]
    assert krx_openapi_probe.category_has_success(details) is False
