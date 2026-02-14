from app.jobs.schedules import build_schedule_map


def test_schedule_contains_core_jobs() -> None:
    schedules = build_schedule_map()
    assert "refresh_corp_master_daily" in schedules
    assert "refresh_ipo_pipeline_hourly" in schedules
    assert "refresh_krx_market_daily" in schedules
