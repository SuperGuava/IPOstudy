# Company Explorer Design (Phase 1)

Date: 2026-02-17
Owner: Antigravity productization stream

## Goal

Expand from IPO-only views into a beginner-friendly company analysis workspace.

## Scope (Phase 1)

1. Add universal company discovery API.
2. Add beginner summary API for one selected company.
3. Add reusable analysis template catalog.
4. Provide a web Explorer page for non-experts.

## API Design

1. `GET /api/v1/insights/companies`
   - inputs: `query`, `limit`
   - output: company list with stage, listing date, quality counts, risk label
2. `GET /api/v1/insights/company`
   - input: `company_key`
   - output: IPO snapshot + quality snapshot + beginner summary + quick insights
3. `GET /api/v1/insights/templates`
   - output: built-in analysis playbooks for non-experts

## Data Strategy

1. Reuse `ipo_pipeline_item` as the default discovery backbone.
2. Reuse `data_quality_issue` for risk and quality aggregates.
3. Use deterministic `company_key`:
   - `corp_code` when available
   - `name:<corp_name>` when `corp_code` is missing

## UX Strategy

1. Left pane: searchable company list.
2. Right pane: beginner summary, quick insights, quality snapshot, analysis templates.
3. Keep language plain and action-oriented.

## Non-goals (Phase 1)

1. Full valuation model or portfolio optimization.
2. Multi-company compare matrix.
3. Natural language chat search.

## Phase 2 Candidates

1. Add financial trend charts and peer comparison.
2. Add saved views and alert subscriptions.
3. Add sector/market-level screening presets.

