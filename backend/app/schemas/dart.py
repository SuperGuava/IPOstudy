from typing import TypedDict


class DartDisclosureItem(TypedDict, total=False):
    corp_code: str
    corp_name: str
    rcept_no: str
    report_nm: str
    rcept_dt: str
    pblntf_ty: str
    pblntf_detail_ty: str


class DartListResponse(TypedDict, total=False):
    status: str
    message: str
    list: list[DartDisclosureItem]


class DartCompanyResponse(TypedDict, total=False):
    status: str
    message: str
    corp_code: str
    corp_name: str
    ceo_nm: str
    corp_cls: str
    induty_code: str
    acc_mt: str
    hm_url: str


class DartEstkRsResponse(TypedDict, total=False):
    status: str
    message: str
    rcept_no: str
    corp_code: str
    corp_name: str
