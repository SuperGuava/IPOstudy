# Web Public Deploy (Plan A: Vercel + Render)

Updated: 2026-02-17

## 0) Architecture

1. Web: Vercel (`web` Next.js app)
2. API: Render (`backend` FastAPI Docker service)
3. DB/Cache: Render Postgres + Redis

## 1) Render API Deploy

1. Open Render Dashboard -> Blueprint deploy
2. Select repo and `render.yaml` at repo root
3. Fill secret env vars on Render:
   - `DART_API_KEY`
   - `KRX_API_KEY`
4. Deploy and wait for health:
   - `/api/v1/health` should return `200`
5. Save backend URL:
   - `https://<render-backend>.onrender.com`

## 2) Vercel Link to Existing Project

1. `cd D:\260214\web`
2. `npx vercel login`
3. `npx vercel link`
   - Scope: `kuhwa-kims-projects`
   - choose existing project

## 3) Vercel Environment Variables

Set both Preview and Production:

1. `API_BASE_URL=https://<render-backend>.onrender.com/api/v1`
2. `NEXT_PUBLIC_API_BASE_URL=https://<render-backend>.onrender.com/api/v1`

CLI example:

1. `npx vercel env add API_BASE_URL production`
2. `npx vercel env add API_BASE_URL preview`
3. `npx vercel env add NEXT_PUBLIC_API_BASE_URL production`
4. `npx vercel env add NEXT_PUBLIC_API_BASE_URL preview`

## 4) Deploy Web

1. `cd D:\260214\web`
2. `npx vercel --prod`

## 5) Smoke Test

1. `https://<vercel-domain>/`
2. `https://<vercel-domain>/explorer`
3. API checks:
   - `https://<render-backend>.onrender.com/api/v1/health`
   - `https://<render-backend>.onrender.com/api/v1/insights/overview`

## 6) Known Blockers

1. If `vercel whoami` fails:
   - run `npx vercel login` first
2. If Vercel page shows stale/failed API data:
   - verify `API_BASE_URL` and `NEXT_PUBLIC_API_BASE_URL` in Vercel project env
3. If Render DB URL starts with `postgres://`:
   - backend already normalizes to `postgresql+psycopg://` automatically

