# Guava Guide

Updated: 2026-02-16
Audience: product owner / 운영 담당 / 다음 세션 개발자

## 1) 현재 상태 한 줄 요약

Anti-Gravity는 MVP를 넘어 제품형 운영 단계까지 올라왔고, 핵심 API/대시보드/품질게이트/KRX 다중 경로 연동이 동작합니다. 남은 핵심 리스크는 ESG 일부 API 권한 승인 대기입니다.

## 2) 지금 동작하는 것

- 백엔드
  - FastAPI + SQLAlchemy + Alembic
  - DB 기반 IPO pipeline API
  - quality API (`/quality/issues`, `/quality/summary`, `/quality/entity/{entity_key}`)
  - export API (`/export/ipo.xlsx`, `/export/company/{corp_code}.xlsx`)
- 데이터 파이프라인
  - DART + KIND + KRX OpenAPI 수집
  - 정규화/매칭/스냅샷 publish + quality gate
  - `refresh=true` 요청 시 실수집 실행
- 프론트
  - Dashboard / IPO Pipeline / Company Snapshot / Quality / Export
  - API 실연동 기반 KPI/그리드/필터/디테일 뷰
  - e2e 테스트 2개 기준 유지

## 3) KRX 연동 현황 (중요)

현재 `.env` 기준 다중 경로 설정 (콤마 구분):

- `KRX_API_INDEX_PATH=idx/krx_dd_trd,idx/kospi_dd_trd,idx/kosdaq_dd_trd`
- `KRX_API_STOCK_PATH=sto/stk_bydd_trd`
- `KRX_API_SECURITIES_PATH=sto/ksq_bydd_trd,sto/ksq_isu_base_info`
- `KRX_API_BOND_PATH=bon/bnd_bydd_trd`
- `KRX_API_DERIVATIVE_PATH=drv/fut_bydd_trd,drv/opt_bydd_trd`
- `KRX_API_GENERAL_PATH=sto/knx_bydd_trd,sto/knx_isu_base_info`
- `KRX_API_ESG_PATH=esg/sri_bond_info,esg/esg_index_info,esg/esg_etp_info`

실행 결과 요약:

- 대부분 카테고리 `OK`
- ESG는 현재 `partial`
  - `esg/sri_bond_info`: OK
  - `esg/esg_index_info`, `esg/esg_etp_info`: 권한 승인 대기

안정화 적용:

- KRX 간헐 `403 Access Denied` 대응 재시도 로직 적용
  - 파일: `backend/app/services/ipo_service.py`

## 4) 새 세션 즉시 시작 명령

1. 인프라
   - `docker compose -f infra/docker-compose.yml up -d`
2. 백엔드
   - `cd backend`
   - `python -m alembic upgrade head`
   - `python -m pytest -q`
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. 웹
   - `cd web`
   - `npm install`
   - `npm run build:stable`
   - `npm run dev -- --port 3000`
4. KRX 상태 확인
   - `cd backend`
   - `python scripts/krx_openapi_probe.py`
5. 실수집 smoke
   - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`

## 5) 주요 문서 위치

- 운영 런북: `docs/operations/runbook.md`
- 실행 이력: `docs/operations/history.md`
- 세션 인수인계: `docs/operations/session-handoff.md`
- 제품화 설계: `docs/plans/2026-02-15-antigravity-productization-design.md`
- 제품화 실행 계획: `docs/plans/2026-02-15-antigravity-productization.md`

## 6) 지금 당장 다음 액션 (우선순위)

1. KRX 포털에서 ESG 두 API 승인 완료 확인
   - `esg/esg_index_info`
   - `esg/esg_etp_info`
2. 승인 직후 검증
   - `python scripts/krx_openapi_probe.py`
   - refresh API 3회 반복 호출
3. ESG status가 `partial` -> `ok:*`로 바뀌는지 확인 후 history 기록

## 7) Git 운영 원칙 (이어개발용)

- 기능/문서/운영 안정화 단위로 커밋 분리
- 임시 로그/빌드 산출물 커밋 금지 (`.gitignore` 반영)
- 권장 흐름
  1. `git checkout -b feat/<topic>`
  2. 작업
  3. `python -m pytest -q` + `npx playwright test` + `npm run build:stable`
  4. 커밋
  5. PR/병합
