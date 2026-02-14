def build_schedule_map() -> dict[str, dict]:
    return {
        "refresh_corp_master_daily": {"cron": "0 2 * * *"},
        "refresh_ipo_pipeline_hourly": {"cron": "0 * * * *"},
        "refresh_krx_market_daily": {"cron": "30 2 * * *"},
        "quality_summary_daily": {"cron": "45 2 * * *"},
    }
