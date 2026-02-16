# Antigravity Productization Design (Phase 4)

Date: 2026-02-15
Owner: Antigravity Web
Status: Approved (auto-advance by user directive)

## 1) Positioning and UX Direction

- Primary target: internal strategy engine users.
- Information density: high-density Bloomberg-lite.
- Product style: institutional intelligence dashboard.
- System choice: Tailwind + shadcn-style component architecture.
- Theme default: dark mode.

## 2) IA and Screen Structure

- Shell layout:
  - left fixed navigation
  - top control bar
  - main analysis surface
  - right detail drawer
- Navigation:
  - Dashboard
  - IPO Pipeline
  - Company Snapshot
  - Quality
  - Export
- IPO Pipeline as core landing workflow:
  - KPI cards (total, offering, pre-listing, listed, refresh)
  - stage distribution strip
  - dense table
  - row-select detail drawer

## 3) Components and State Model

- App shell:
  - `AppShell` (sidebar + topbar + content slot)
  - `SidebarNav`
  - `TopControlBar`
- IPO screen:
  - `IpoKpiStrip`
  - `IpoStageStrip`
  - `IpoDataGrid`
  - `IpoDetailDrawer`
  - `SourceStatusBadge`
- Data state:
  - `items`: pipeline rows from backend
  - `selectedPipelineId`: local UI state for drawer
  - `refreshMeta`: optional backend refresh result
  - derived counters by stage

## 4) Data Flow and API Contract

- Primary API source:
  - `GET /api/v1/ipo/pipeline`
  - `GET /api/v1/ipo/pipeline?refresh=true&corp_code=<x>&bas_dd=<yyyymmdd>`
  - `GET /api/v1/ipo/{pipeline_id}`
- Frontend strategy:
  - server fetch for initial paint
  - client state for row selection and drawer interaction
  - form-driven refresh via query params (idempotent)

## 5) Error Handling and Empty States

- API failure:
  - render compact alert banner with retry action
- Empty pipeline:
  - render zero-state panel with refresh CTA
- Partial source health:
  - show color-coded source badges from refresh metadata

## 6) Visual Language

- Palette:
  - background: `#0f172a`
  - card: `#111827`
  - accent: `#22d3ee`
  - success: `#10b981`
  - warning: `#f59e0b`
  - error: `#ef4444`
- Typography:
  - small but readable (13px/14px for data-heavy rows)
  - mono accents for ids and numeric metadata
- Motion:
  - subtle load-in for KPI cards
  - stagger reveal for grid rows

## 7) Testing Strategy

- Backend API regression:
  - existing `pytest` suite must remain green
- Web:
  - update Playwright flow to assert new pipeline/dashboard markers
  - verify mobile and desktop viewport rendering path
- Completion gate:
  - backend tests, web tests, e2e tests all pass

## 8) Non-goals for This Phase

- No chart-heavy analytics stack integration yet.
- No auth/tenant boundary implementation.
- No full design token package publication.

