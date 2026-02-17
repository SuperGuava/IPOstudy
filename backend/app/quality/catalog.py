from __future__ import annotations

from typing import TypedDict


class QualityRuleMeta(TypedDict):
    rule_code: str
    source: str
    severity: str
    title: str
    description: str
    operator_action: str


RULE_CATALOG: list[QualityRuleMeta] = [
    {
        "rule_code": "COMMON_REQUIRED_KEYS",
        "source": "COMMON",
        "severity": "FAIL",
        "title": "Required fields are missing",
        "description": "A required field was empty or missing in the source payload.",
        "operator_action": "Check source response payload and parser mapping for dropped keys.",
    },
    {
        "rule_code": "DART_RCEPT_NO_FORMAT",
        "source": "DART",
        "severity": "FAIL",
        "title": "DART receipt number format error",
        "description": "rcept_no should be a 14-digit identifier.",
        "operator_action": "Verify DART API response and normalize invalid rcept_no values.",
    },
    {
        "rule_code": "DART_REPORT_NAME_EMPTY",
        "source": "DART",
        "severity": "WARN",
        "title": "DART report name is empty",
        "description": "A filing row exists but report_nm is empty.",
        "operator_action": "Review raw disclosure row and fallback report name mapping.",
    },
    {
        "rule_code": "KIND_STAGE_ALLOWED",
        "source": "KIND",
        "severity": "FAIL",
        "title": "KIND stage is not supported",
        "description": "stage value is outside the supported IPO stage set.",
        "operator_action": "Update KIND stage mapping or parser if schema changed.",
    },
    {
        "rule_code": "KIND_KEY_DATE_REQUIRED",
        "source": "KIND",
        "severity": "WARN",
        "title": "KIND key date missing",
        "description": "No listing/subscription/demand forecast date found for the row.",
        "operator_action": "Validate date columns from KIND and parser column offsets.",
    },
    {
        "rule_code": "KRX_REQUIRED_PARAMS",
        "source": "KRX",
        "severity": "FAIL",
        "title": "KRX required request params missing",
        "description": "Required API request parameters were not provided.",
        "operator_action": "Check configured KRX path requirements and request_params mapping.",
    },
    {
        "rule_code": "KRX_RESPONSE_SCHEMA",
        "source": "KRX",
        "severity": "FAIL",
        "title": "KRX response schema mismatch",
        "description": "OutBlock_1 was missing from KRX response payload.",
        "operator_action": "Inspect raw KRX response and adjust schema parser.",
    },
    {
        "rule_code": "KRX_EMPTY_DATA",
        "source": "KRX",
        "severity": "WARN",
        "title": "KRX returned empty rows",
        "description": "OutBlock_1 exists but row list is empty.",
        "operator_action": "Retry with a valid basDd and confirm API approval scope.",
    },
    {
        "rule_code": "KRX_BAS_DD_MISMATCH",
        "source": "KRX",
        "severity": "WARN",
        "title": "KRX row date mismatch",
        "description": "Returned BAS_DD differs from the requested basDd.",
        "operator_action": "Confirm API behavior for non-trading days and adjust basDd input.",
    },
    {
        "rule_code": "KRX_DUPLICATE_ISU_CD",
        "source": "KRX",
        "severity": "WARN",
        "title": "KRX duplicate ISU code rows",
        "description": "Duplicate ISU_CD values were detected in the same payload.",
        "operator_action": "Deduplicate rows before publish and inspect endpoint semantics.",
    },
    {
        "rule_code": "KRX_NUMERIC_FIELD_INVALID",
        "source": "KRX",
        "severity": "WARN",
        "title": "KRX numeric field parse issue",
        "description": "Numeric columns include non-numeric values.",
        "operator_action": "Adjust numeric sanitization for commas/sign/placeholder patterns.",
    },
    {
        "rule_code": "CROSS_KIND_DART_LINKAGE_RATIO",
        "source": "CROSS",
        "severity": "WARN",
        "title": "KIND-DART linkage ratio is low",
        "description": "Name linkage ratio between KIND and DART rows is below threshold.",
        "operator_action": "Review corp_name normalization and matching strategy.",
    },
    {
        "rule_code": "CROSS_POST_LISTING_KRX_ATTACH",
        "source": "CROSS",
        "severity": "WARN",
        "title": "Listed items without KRX attachment",
        "description": "Listed KIND rows were found, but no KRX rows were attached.",
        "operator_action": "Check KRX connectivity, permissions, and date parameters.",
    },
]

