## Anti-Gravity 전달용: DART + KRX + KIND 기반 “IPO/기업정보 Fast Fetch” 시스템 구축 계획 및 지침

### 1) 목표

1. **IPO 관련 기업**(예비심사 → 증권신고서 → 수요예측/청약 → 상장예정/신규상장)의 **전체 파이프라인을 한 화면/한 API로 조회**
2. 특정 기업의 **최신 공시, 핵심 재무제표/지표, 기업개황, 원문(증권신고서 등)까지** 빠르게 가져오기
3. 시장데이터는 **KRX 원천 데이터(시가총액/지수/투자자/공매도 등)**를 최대한 활용하고, 필요한 경우에만 보완 소스(예: 실시간 호가/체결 대체) 사용

> 핵심 원칙: **“검색/크롤링으로 오래된 자료를 가져오지 말고, DART·KRX·KIND ‘원천’ API/데이터 호출을 표준화한다.”**

---

## 2) 데이터 소스(원천) 및 역할 분담

### A. DART OpenAPI (금감원 OPENDART)

* 목적: **공시 기반 ‘기업 최신정보의 정답지(SSOT)’**
* 활용 범위

  * 공시 목록 검색: 최신 공시 추적, 정정 포함 “최종본” 기준 추적 ([OPENDART][1])
  * 기업개황(회사 기본정보): 대표자/업종/결산월/홈페이지 등 ([OPENDART][2])
  * 고유번호(법인 마스터): corp_code–stock_code 매핑의 기준 ([OPENDART][3])
  * 공시 원문 다운로드(Zip/XML): **증권신고서/정정신고서 원문 확보** ([OPENDART][4])
  * 재무제표/지표:

    * 단일회사 주요계정 ([OPENDART][5])
    * 단일회사 전체 재무제표 ([OPENDART][6])
    * 단일회사 주요 재무지표 ([OPENDART][7])
  * IPO 핵심(증권신고서 주요정보 – 지분증권): IPO/공모 핵심 요약 필드 추출 ([OPENDART][8])

또한 OPENDART는 공시 원문(XML) 다운로드 및 주요 공시/재무 정보를 데이터 형태로 제공하는 것을 명시합니다. ([OPENDART][9])

---

### B. KRX Data Marketplace (data.krx.co.kr)

* 목적: **시장/거래 데이터의 원천(지수, 주식, 채권, 파생, ESG 등)**
* 활용 범위

  * 시가총액/거래대금/거래량/지수/투자자별 매매동향 등 시장지표 ([KRX 데이터 시스템][10])
  * (기존 구현처럼) 내부 JSON 엔드포인트 기반 수집:

```text
POST https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd
```

* 지침: “KRX는 카테고리별 bld(빌드 ID)가 다양하므로, **데이터셋 레지스트리(메타 테이블)로 관리**” (아래 6~7절 참조)

---

### C. KRX KIND (상장/IPO/공모/예비심사 정보)

* 목적: **IPO 파이프라인의 진행상태/일정/상장예정/신규상장 ‘거래소 표준’**
* 활용 범위(대표 화면)

  * 예비심사기업 ([KIND][11])
  * 공모기업현황(수요예측/청약/납입/확정공모가/상장예정일 등) ([KIND][12])
  * 신규상장기업현황 ([KIND][13])
  * 공모일정 ([KIND][14])

> **IPO 파이프라인 정합성 전략**
>
> * “진행상태/일정”: KIND 우선(거래소 공시채널)
> * “신고서/정정/원문”: DART 우선(금감원 공시 원문)
> * “상장 이후 거래데이터”: KRX Data 우선(시가총액/거래/지수/수급)

---

## 3) 제품/기능 요구사항(Use Cases)

### 3.1 IPO 중심 핵심 기능

1. **IPO 파이프라인 리스트**

   * 필터: 시장(코스피/코스닥/코넥스), 업종, 주관사, 기간, SPAC 여부
   * 상태: 예비심사 → 신고서제출 → 수요예측 → 청약 → 납입 → 상장예정 → 신규상장(완료)
2. **IPO 딜 상세 페이지(회사 단위)**

   * 일정(수요예측/청약/상장예정일)
   * 확정공모가/공모금액/주관사
   * DART 증권신고서(지분증권) 요약 + 원문 다운로드/미리보기 링크
   * 재무 하이라이트(최근 3개년도/분기 핵심지표)

### 3.2 기업 “Fast Snapshot” (초고속 기업 카드)

* 입력: 회사명 / 종목코드(6자리) / corp_code(8자리)
* 출력(단일 API 응답으로)

  * 기업개황(대표자/업종/결산월/홈페이지 등)
  * 최신 공시 Top N(정정 포함 최종본 기준)
  * 최근 재무제표(요약 손익/재무상태, 주요지표)
  * KRX 시가총액/거래대금/수급(가능한 범위)

---

## 4) 권장 아키텍처(“빠르게 가져오기”를 위한 구성)

### 4.1 레이어 구조

1. **Connector Layer (수집 커넥터)**

   * dart_connector
   * krx_market_connector
   * kind_ipo_connector
2. **Raw Store (원문/원시응답 저장)**

   * JSON/XML/Zip 원본을 그대로 저장(재현성/감사 추적)
3. **Normalized Store (정규화 테이블)**

   * 기업 마스터, 공시, 재무, IPO 이벤트, 시장데이터
4. **Serving API**

   * `/company/snapshot`
   * `/ipo/pipeline`
   * `/ipo/{id}`
   * `/company/{corp_code}/financials`
5. **UI(선택)**

   * IPO 리스트/딜 상세/기업 스냅샷/다운로드(Excel)

### 4.2 성능 원칙

* “사용자 요청 시 매번 전부 호출” 금지
  → **증분 수집 + 캐시 + 사전 계산(materialized snapshot)**이 기본
* “최신”은 DART list로 트리거
  → 신규/정정 공시를 감지하면 해당 기업 스냅샷만 갱신

---

## 5) 데이터 모델(최소 스키마 제안)

### 5.1 기업 마스터

* `corp_master`

  * corp_code (PK)
  * stock_code (nullable; 상장 전/비상장 대비)
  * corp_name, eng_name
  * modify_date (DART corpCode 기준)
  * market_cls(KOSPI/KOSDAQ/KONEX/ETC)

### 5.2 공시

* `dart_disclosure`

  * rcept_no (PK)
  * corp_code, report_nm, rcept_dt, flr_nm
  * pblntf_ty, pblntf_detail_ty
  * is_final(last_reprt_at로 수집했는지), is_amended(정정 여부)

### 5.3 재무

* `dart_fin_major_accounts` (요약)
* `dart_fin_full_accounts` (전체 계정)
* `dart_fin_indicators` (주요 지표)

### 5.4 IPO

* `ipo_pipeline_item`

  * pipeline_id (PK)
  * corp_name, corp_code(nullable), expected_stock_code(nullable)
  * stage(예비심사/공모/상장예정/신규상장)
  * key_dates(수요예측/청약/상장예정일 등)
  * offer_price, offer_amount, lead_manager
  * source_kind_row_id / source_dart_rcept_no 매핑

---

## 6) DART API 업그레이드 지침(필수)

### 6.1 “기업 마스터(고유번호)”를 시스템의 기준으로

* DART 고유번호는 Zip(binary)로 내려오며, 내부 XML에 `corp_code`, `stock_code`, `modify_date` 등이 포함됩니다. ([OPENDART][3])
* 운영 지침

  * 주기적으로(일/주 단위) 다운로드 → 파싱 → `corp_master` 갱신
  * `modify_date`가 바뀐 기업만 후속(company, 재무 등) 재수집
  * stock_code가 없는 corp_code(비상장/상장 전)도 **IPO 파이프라인용으로 유지**

### 6.2 기업개황(company)로 “회사 카드” 기본정보 확보

* 기업개황 요청URL(예: JSON) ([OPENDART][2])

```text
GET https://opendart.fss.or.kr/api/company.json
```

* 저장/표준화

  * 대표자, 업종코드, 설립일, 결산월, 홈페이지/IR URL 등은 `corp_profile`로 분리 저장 권장

### 6.3 공시검색(list)로 “최신”을 트리거

* 공시검색 요청URL ([OPENDART][1])

```text
GET https://opendart.fss.or.kr/api/list.json
```

* 핵심 파라미터 운용

  * `last_reprt_at=Y` 중심 운용(정정/최종본 기준 스냅샷 안정화)
  * IPO 탐지용 필터: `pblntf_ty=C`(발행공시) + 상세유형(C001 등) ([OPENDART][1])

    * C001: 증권신고(지분증권) 등 (세부코드 표는 DART 개발가이드 기준)

### 6.4 공시 원문(document)로 “IPO 원문/정정” 확보

* 공시서류원본파일(document.xml) 요청URL ([OPENDART][4])

```text
GET https://opendart.fss.or.kr/api/document.xml
```

* 지침

  * rcept_no 기준으로 원문 Zip 저장 (raw store)
  * Zip 내부 XML/HTML 구조 파싱은 “필요 필드만 추출”하는 방식으로 최소화(전체 텍스트 OCR 같은 고비용 처리 지양)

### 6.5 IPO 요약 필드: “증권신고서(지분증권) 주요정보” 우선 적용

* 지분증권(증권신고서 주요정보) 요청URL ([OPENDART][8])

```text
GET https://opendart.fss.or.kr/api/estkRs.json
```

* 전략

  * IPO 기업은 **신고서 원문 파싱보다 먼저** `estkRs` 요약 API로 “가격/수량/주요조건/주요일자” 등을 구조화
  * 원문(document)은 **검증/첨부자료/상세추출용**으로 사용(2단계)

### 6.6 재무제표: “요약→전체” 2단계로

* 초고속 스냅샷에는 “요약(major) + 지표”로 충분

  * 단일회사 주요계정 ([OPENDART][5])
  * 단일회사 주요 재무지표 ([OPENDART][7])
* 필요 시(사용자가 drill-down) 전체 재무제표 호출

  * 단일회사 전체 재무제표 ([OPENDART][6])

---

## 7) KRX Data Marketplace 심화 연결 지침(필수)

### 7.1 내부 JSON 엔드포인트 표준화

* 기존에 확인된 내부 호출 방식 유지:

```text
POST https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd
```

* 구현 지침(중요)

  1. **Dataset Registry(메타 테이블) 구축**

     * `dataset_key`, `bld`, `required_params`, `market_scope`, `desc`, `sample_response_schema`
  2. “지수/주식/채권/파생/ESG…” 카테고리를 dataset_key로 그룹화
  3. bld 변경/폐기 대비:

     * 매일/매주 “헬스체크”로 404/스키마 변경 감지 → 알림

KRX Data Marketplace는 거래소의 Marketdata/투자분석정보 등을 통합 제공하는 데이터 플랫폼임을 명시합니다. ([KRX 데이터 시스템][15])

### 7.2 우선 확장 순서(IPO/기업분석 관점)

1. **주식(상장종목, 시가총액, 거래대금/거래량)**
2. **투자자별 매매동향(수급)**
3. **지수(시장 대비 상대성과/상관 분석 기반)**
4. **공매도/대차/리스크 지표(가능한 범위)**
5. **ESG/지배구조(가능한 범위)**

---

## 8) KIND(IPO) 연동 지침(IPO 파이프라인의 “상태/일정” 담당)

### 8.1 KIND를 “IPO Stage의 원천”으로 사용

* 예비심사기업 ([KIND][11])
* 공모기업현황(일정/공모가/공모금액/상장예정일 등) ([KIND][12])
* 공모일정 ([KIND][14])
* 신규상장기업현황(상장 완료) ([KIND][13])

### 8.2 데이터 결합(매칭) 규칙

* 1차 키: `corp_name(정규화)` + `신고서제출일/청약일정/상장예정일 중 하나`
* 2차 키: DART에서 `pblntf_ty=C` 공시 중 report_nm에 “증권신고서” 계열이 있는지 확인
* 3차 키: 상장 이후 `stock_code`가 확정되면 `corp_master.stock_code`로 최종 통합

### 8.3 “IPO 원클릭” 결과물 정의

* 한 기업을 클릭하면:

  * KIND: 현재 stage + 일정 + 공모 관련 숫자
  * DART: 관련 rcept_no 묶음(최초/정정/첨부) + estkRs 요약 + 원문(document) 링크
  * 상장 후: KRX 시총/거래/수급 자동 연결

---

## 9) 데이터 품질/정합성(반드시 넣을 것)

### 9.1 원천 간 Cross-check

* DART stock_code ↔ KRX 종목코드 목록
* IPO 일정(KIND) ↔ DART 신고서 접수일/정정 여부
* “정정” 존재 시 DART `last_reprt_at=Y` 기준으로 최신본만 스냅샷에 노출

### 9.2 변경 추적(필수)

* 공시는 “정정/첨부추가”가 잦음
  → `rcept_no`를 버전 체인으로 묶고, 스냅샷은 “최종본”만

---

## 10) 보안/키 관리 지침(강제)

1. **API Key는 코드/문서에 하드코딩 금지**

   * 환경변수: `DART_API_KEY`, `KRX_API_KEY`
   * Secret Manager(권장) 사용
2. 호출 로그에는 Key 마스킹
3. 배포 환경별 Key 분리(개발/스테이징/운영)

---

## 11) 운영/모니터링 지침

* 헬스체크

  * DART: list/company/financial 3종 “샘플 기업”으로 정상 응답 확인
  * KRX: 핵심 dataset bld 5~10개 주기적 확인
  * KIND: IPO 4개 페이지 파싱 성공률/행 수 변화 감지
* 알림 트리거

  * 스키마 컬럼 변동(신규/삭제/명 변경)
  * 응답 status 에러 코드 누적(요청 제한/차단 등)
  * 데이터 공백(예: 특정 시장/기간 레코드 0)

---

## 12) Anti-Gravity 최종 산출물(Deliverables) & 인수 기준

### 12.1 산출물

1. **Connector SDK (Python 패키지 권장)**

   * `dart_connector`, `krx_connector`, `kind_connector`
2. **정규화 ETL + 스냅샷 빌더**
3. **Serving API**

   * IPO 파이프라인, 기업 스냅샷, 재무/공시 drill-down
4. (선택) **대시보드 UI**

   * IPO 보드 / 기업 카드 / 원문 다운로드 / Excel Export

### 12.2 인수 기준(예시)

* [ ] 회사명으로 검색 시 `corp_code` 매핑이 안정적으로 동작
* [ ] IPO 후보(예비심사/공모/상장예정/신규상장) 목록이 KIND 기반으로 재현
* [ ] IPO 딜 상세에서 DART 신고서 요약(estkRs) + 원문(document)까지 연결
* [ ] 기업 스냅샷 호출 1회로 “기업개황 + 최신공시 + 최근 재무요약 + (가능시) KRX 시총/수급” 반환
* [ ] DART/ KR X / KIND 중 1개 소스 장애 시에도 **부분 응답 + 원인 로깅**이 제공

---

## 부록: Anti-Gravity 개발자용 “최소 예시 흐름(IPO 기업 1개를 끝까지)”

1. KIND에서 공모기업 1건을 가져온다(회사명/신고서제출일/상장예정일 등). ([KIND][12])
2. 회사명으로 DART corp_master에서 corp_code 후보를 찾는다(없으면 corpCode Zip 최신본에서 재탐색). ([OPENDART][3])
3. DART list에서 `pblntf_ty=C` 및 상세유형(증권신고 계열)로 rcept_no를 찾는다. ([OPENDART][1])
4. rcept_no로 `estkRs` 요약을 가져와 구조화한다. ([OPENDART][8])
5. rcept_no로 document 원문(zip)을 저장하고(필요시) 추가 필드를 추출한다. ([OPENDART][4])
6. 상장 후에는 stock_code로 KRX 데이터셋을 붙여 “상장 이후 퍼포먼스/수급”을 자동 노출한다. ([KRX 데이터 시스템][15])

---

원하시면, 위 지침을 기반으로 Anti-Gravity가 바로 개발에 들어갈 수 있도록 **내부 API 스펙(OpenAPI YAML 형태)**(예: `/ipo/pipeline`, `/company/snapshot` 응답 스키마까지)도 같은 톤으로 한 번에 정리해드릴게요.

[1]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001&utm_source=chatgpt.com "전자공시 OPENDART 시스템 | 개발가이드 | 상세 - FSS"
[2]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002&utm_source=chatgpt.com "개발가이드 - 공시정보 - 기업개황 - 전자공시 OPENDART 시스템"
[3]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019018&utm_source=chatgpt.com "개발가이드 - 공시정보 - 고유번호 - 전자공시 OPENDART 시스템"
[4]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019003&utm_source=chatgpt.com "개발가이드 - 공시정보 - 공시서류원본파일 - OPENDART"
[5]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019016&utm_source=chatgpt.com "개발가이드 - 정기보고서 재무정보 - 전자공시 OPENDART 시스템"
[6]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020&utm_source=chatgpt.com "개발가이드 - 정기보고서 재무정보 - OPEN DART"
[7]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2022001&utm_source=chatgpt.com "개발가이드 - 정기보고서 재무정보 - OPENDART - 금융감독원"
[8]: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS006&apiId=2020054&utm_source=chatgpt.com "개발가이드 - 증권신고서 주요정보 - 전자공시 OPENDART 시스템"
[9]: https://opendart.fss.or.kr/intro/main.do?utm_source=chatgpt.com "오픈API 소개"
[10]: https://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd?utm_source=chatgpt.com "종목검색 - KRX Data Marketplace - 한국거래소"
[11]: https://kind.krx.co.kr/listinvstg/listinvstgcom.do?method=searchListInvstgCorpMain&utm_source=chatgpt.com "예비심사기업"
[12]: https://kind.krx.co.kr/listinvstg/pubofrprogcom.do?method=searchPubofrProgComMain&utm_source=chatgpt.com "공모기업현황"
[13]: https://kind.krx.co.kr/listinvstg/listingcompany.do?method=searchListingTypeMain&utm_source=chatgpt.com "신규상장기업현황"
[14]: https://kind.krx.co.kr/listinvstg/pubofrschdl.do?method=searchPubofrScholMain&utm_source=chatgpt.com "공모일정"
[15]: https://data.krx.co.kr/?utm_source=chatgpt.com "KRX Data Marketplace - 한국거래소"
