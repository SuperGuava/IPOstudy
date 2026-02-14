from unittest.mock import Mock

from app.jobs.tasks import enqueue_refresh_for_disclosure


def test_dart_trigger_enqueues_company_refresh() -> None:
    refresh = Mock()
    enqueue_refresh_for_disclosure({"corp_code": "00126380"}, refresh_fn=refresh)
    refresh.assert_called_once_with("00126380")
