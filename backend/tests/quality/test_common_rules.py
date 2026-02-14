from app.quality.rules.common import check_date_format, check_numeric, check_required_keys


def test_required_key_rule_fails_when_missing() -> None:
    issues = check_required_keys({"corp_name": "alpha"}, ["corp_code"])
    assert issues
    assert issues[0].severity == "FAIL"
    assert issues[0].rule_code == "COMMON_REQUIRED_KEYS"


def test_date_format_rule_accepts_valid_formats() -> None:
    assert check_date_format("20260214")
    assert check_date_format("2026-02-14")
    assert not check_date_format("2026/02/14")


def test_numeric_rule_validates_negative_policy() -> None:
    assert check_numeric("10")
    assert check_numeric("-10", allow_negative=True)
    assert not check_numeric("-10", allow_negative=False)
