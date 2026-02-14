from sqlalchemy import inspect


def test_quality_tables_exist(db_engine) -> None:
    expected = {
        "data_quality_issue",
        "data_quality_summary_daily",
        "snapshot_publish_log",
    }
    assert expected.issubset(set(inspect(db_engine).get_table_names()))
