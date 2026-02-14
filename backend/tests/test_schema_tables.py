from sqlalchemy import inspect


def test_core_tables_exist(db_engine) -> None:
    expected = {
        "corp_master",
        "corp_profile",
        "dart_disclosure",
        "ipo_pipeline_item",
        "company_snapshot",
        "ipo_pipeline_snapshot",
        "dataset_registry",
        "raw_payload_log",
    }
    assert expected.issubset(set(inspect(db_engine).get_table_names()))
