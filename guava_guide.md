# Guava Guide

Updated: 2026-02-17
Audience: product owner / 운영 담당 / 다음 세션 개발자

## 1) 현재 상태 한 줄 요약

Anti-Gravity는 제품형 운영 단계이며, 최근 이슈였던 "IPO 회사가 1개만 보임" 문제를 해결해 refresh 기준 `2301`건이 적재되는 상태입니다.

## 2) 지금 동작하는 것

- 백엔드
  - FastAPI + SQLAlchemy + Alembic
  - DB 기반 IPO pipeline API
  - quality API (`/quality/issues`, `/quality/summary`, `/quality/overview`, `/quality/entity/{entity_key}`)
  - export API (`/export/ipo.xlsx`, `/export/company/{corp_code}.xlsx`)
- 데이터 파이프라인
  - DART + KIND + KRX OpenAPI 수집
  - 정규화/매칭/스냅샷 publish + quality gate
  - `refresh=true` 요청 시 실수집 실행
- 프론트
  - Dashboard / IPO Pipeline / Company Snapshot / Quality / Export
  - API 실연동 기반 KPI/그리드/필터/디테일 뷰
  - e2e 테스트 유지

## 3) 최근 핵심 수정: 회사가 1개만 보이던 원인

원인:

1. KIND는 메인 페이지가 아니라 내부 `Sub` 요청 응답에 실제 행 데이터가 존재합니다.
2. 기존 로직은 메인 페이지 파싱 기준이라 `kind_rows=0`이 발생했습니다.
3. 초기 demo seed(`alpha-tech`)가 남아 있을 수 있어 1건만 보이는 증상이 있었습니다.

해결:

1. KIND 커넥터를 `searchPubofrProgComSub` POST 흐름으로 변경
2. KIND 파서 보강(신규/레거시 테이블 모두 파싱)
3. publish 시 기존 스냅샷 전체 교체(replace)로 demo 잔존 제거

검증:

1. `cd backend && python -m pytest -q` -> `67 passed`
2. `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131` -> `total=2301`, `published=true`
3. `GET /api/v1/ipo/pipeline` -> `alpha-tech` 미존재

## 4) KRX 연동 현황

현재 `.env` 기준 다중 경로 설정 (콤마 구분):

- `KRX_API_INDEX_PATH=idx/krx_dd_trd,idx/kospi_dd_trd,idx/kosdaq_dd_trd`
- `KRX_API_STOCK_PATH=sto/stk_bydd_trd`
- `KRX_API_SECURITIES_PATH=sto/ksq_bydd_trd,sto/ksq_isu_base_info`
- `KRX_API_BOND_PATH=bon/bnd_bydd_trd`
- `KRX_API_DERIVATIVE_PATH=drv/fut_bydd_trd,drv/opt_bydd_trd`
- `KRX_API_GENERAL_PATH=sto/knx_bydd_trd,sto/knx_isu_base_info`
- `KRX_API_ESG_PATH=esg/sri_bond_info,esg/esg_index_info,esg/esg_etp_info`

현황 요약:

1. 대부분 카테고리 `OK`
2. ESG는 `partial` (일부 권한 승인 대기 가능)

## 5) 새 세션 즉시 시작 명령 (비전문가용)

1. 인프라
   - `docker compose -f infra/docker-compose.yml up -d`
2. 백엔드
   - `cd backend`
   - `python -m alembic upgrade head`
   - `python -m pytest -q`
   - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. 웹
   - `cd web`
   - `npm install`
   - `npm run build:stable`
   - `npm run dev -- -p 3000`
4. KRX 상태 확인
   - `cd backend`
   - `python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg`
5. 실수집 smoke
   - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380&bas_dd=20250131`

## 6) 주요 문서 위치

- 운영 런북: `docs/operations/runbook.md`
- 실행 이력: `docs/operations/history.md`
- 세션 인수인계: `docs/operations/session-handoff.md`
- 제품화 설계: `docs/plans/2026-02-15-antigravity-productization-design.md`
- 제품화 실행 계획: `docs/plans/2026-02-15-antigravity-productization.md`

## 7) 다음 액션 (우선순위)

1. ESG 승인 완료 확인
   - `esg/esg_index_info`
   - `esg/esg_etp_info`
2. 승인 직후 검증
   - `python scripts/krx_openapi_probe.py --repeat 5 --bas-dd 20250131 --strict-categories stock,esg`
   - refresh API 5회 반복 호출
3. ESG status가 `partial` -> `ok:*`로 바뀌는지 `history.md` 기록

## 8) Git 운영 원칙 (이어개발용)

- 기능/문서/운영 안정화 단위로 커밋 분리
- 임시 로그/빌드 산출물 커밋 금지 (`.gitignore` 반영)
- 권장 흐름
  1. `git checkout -b feat/<topic>`
  2. 작업
  3. `python -m pytest -q` + `npx playwright test` + `npm run build:stable`
  4. 커밋
  5. PR/병합
