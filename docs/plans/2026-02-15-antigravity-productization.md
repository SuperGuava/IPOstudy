# Antigravity Productization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade the current minimal web UI into a product-like internal strategy dashboard with dense IPO workflow visualization and live refresh controls.

**Architecture:** Keep backend API contract intact and use server-side data fetch + client-side interaction pattern in Next.js. Introduce a dashboard shell, KPI/stage/table/drawer workflow, and dark institutional visual system with Tailwind utility styling and shadcn-style primitives.

**Tech Stack:** Next.js 15 (App Router), TypeScript, Tailwind CSS, Playwright, existing FastAPI API.

---

### Task 1: Bootstrap UI Foundation (Tailwind + Global Theme)

**Files:**
- Modify: `web/package.json`
- Create: `web/postcss.config.js`
- Create: `web/tailwind.config.ts`
- Create: `web/app/globals.css`
- Modify: `web/app/layout.tsx`

**Step 1: Write the failing test**

- Update e2e expectation to require app shell marker that does not exist yet.

**Step 2: Run test to verify it fails**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: FAIL due missing shell marker.

**Step 3: Write minimal implementation**

- Add Tailwind toolchain.
- Add global dark theme tokens and baseline layout classes.
- Add layout-level shell marker and typography setup.

**Step 4: Run test to verify it passes**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: PASS.

**Step 5: Commit**

```bash
git add web/package.json web/postcss.config.js web/tailwind.config.ts web/app/globals.css web/app/layout.tsx web/tests/e2e/ipo-flow.spec.ts
git commit -m "feat(web): bootstrap dark dashboard foundation with tailwind"
```

### Task 2: Implement App Shell and Navigation

**Files:**
- Create: `web/components/ui/card.tsx`
- Create: `web/components/ui/badge.tsx`
- Create: `web/components/app-shell.tsx`
- Modify: `web/app/page.tsx`
- Modify: `web/app/ipo/page.tsx`
- Modify: `web/app/company/[corpCode]/page.tsx`
- Modify: `web/app/ipo/[pipelineId]/page.tsx`

**Step 1: Write the failing test**

- Add assertions for sidebar menu labels and topbar visibility.

**Step 2: Run test to verify it fails**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: FAIL for missing nav/topbar.

**Step 3: Write minimal implementation**

- Build fixed sidebar + top control bar.
- Place all existing pages into same shell.

**Step 4: Run test to verify it passes**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: PASS.

**Step 5: Commit**

```bash
git add web/components web/app web/tests/e2e/ipo-flow.spec.ts
git commit -m "feat(web): add product shell with strategy navigation"
```

### Task 3: Build IPO Product Core Surface (KPI + Stage + Grid + Drawer)

**Files:**
- Modify: `web/lib/api.ts`
- Modify: `web/components/ipo-board.tsx`
- Modify: `web/components/ipo-detail.tsx`
- Modify: `web/components/company-card.tsx`
- Create: `web/components/ipo/ipo-kpi-strip.tsx`
- Create: `web/components/ipo/ipo-stage-strip.tsx`
- Create: `web/components/ipo/ipo-data-grid.tsx`
- Create: `web/components/ipo/ipo-detail-drawer.tsx`

**Step 1: Write the failing test**

- Add checks for KPI strip and stage distribution labels.

**Step 2: Run test to verify it fails**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: FAIL because KPI/stage UI not present.

**Step 3: Write minimal implementation**

- Replace static frontend data with backend fetches.
- Compute stage counters from API items.
- Add row click -> drawer open interaction.
- Show refresh metadata/status if present.

**Step 4: Run test to verify it passes**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: PASS.

**Step 5: Commit**

```bash
git add web/lib/api.ts web/components web/app/ipo/page.tsx web/tests/e2e/ipo-flow.spec.ts
git commit -m "feat(web): implement dense ipo strategy surface with drawer"
```

### Task 4: Wire Refresh Controls and Source Status UX

**Files:**
- Modify: `web/app/ipo/page.tsx`
- Modify: `web/components/ipo-board.tsx`
- Modify: `web/lib/api.ts`
- Modify: `web/tests/e2e/ipo-flow.spec.ts`

**Step 1: Write the failing test**

- Add test for refresh query controls and source status badge rendering.

**Step 2: Run test to verify it fails**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: FAIL for missing refresh/source status markers.

**Step 3: Write minimal implementation**

- Add compact refresh form (`corp_code`, `bas_dd`) and submit.
- Render source status badges from refresh metadata.
- Keep layout responsive for mobile and desktop.

**Step 4: Run test to verify it passes**

Run: `cd web && npx playwright test tests/e2e/ipo-flow.spec.ts`  
Expected: PASS.

**Step 5: Commit**

```bash
git add web/app/ipo/page.tsx web/components/ipo-board.tsx web/lib/api.ts web/tests/e2e/ipo-flow.spec.ts
git commit -m "feat(web): add refresh controls and source status badges"
```

### Task 5: Final Verification and Docs Sync

**Files:**
- Modify: `README.md`
- Modify: `docs/operations/runbook.md`
- Modify: `docs/operations/history.md`

**Step 1: Write the failing test**

- N/A (docs + verification task).

**Step 2: Run verification commands**

Run:
- `cd backend && python -m pytest -q`
- `cd web && npm test -- --runInBand`
- `cd web && npx playwright test`

Expected: all pass.

**Step 3: Update docs**

- Add product UI run/check steps and current status in history.

**Step 4: Re-run verification**

Run same commands above.  
Expected: all pass.

**Step 5: Commit**

```bash
git add README.md docs/operations/runbook.md docs/operations/history.md
git commit -m "docs: add productized dashboard operation notes"
```

### Global Verification Checklist

- `cd backend && python -m pytest -q`
- `cd web && npm test -- --runInBand`
- `cd web && npx playwright test`
- `GET /api/v1/ipo/pipeline`
- `GET /api/v1/ipo/pipeline?refresh=true&corp_code=00126380`
