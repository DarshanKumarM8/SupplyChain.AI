# SupplyChainAI Backend — Deployment & Incident Response Runbook

> **Target platform:** Render (Web Service)
> **Runtime:** Python 3.11 · FastAPI · Uvicorn
> **Branch:** `main` (production)

---

## 1. Environment Variables

All secrets are configured in the **Render Dashboard → Environment** tab.
**Never commit credentials to Git.**

| Variable | Example Value | Required | Notes |
|---|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/supplychainai` | ✅ | Render provides this automatically if you attach a Render Postgres instance. Ensure the `+asyncpg` dialect prefix is present. |
| `REDIS_URL` | `redis://red-xxxx:6379` | ✅ | Provided by Render Redis. Used by Celery broker/backend and caching. |
| `PORT` | *(set by Render)* | ✅ | Injected automatically — do **not** set manually. The Dockerfile reads it via `${PORT:-8000}`. |
| `DEBUG` | `false` | ❌ | Set to `false` in production to disable SQLAlchemy echo and verbose logging. |

### Verifying Variables

```bash
# SSH into the Render shell (if enabled) and confirm:
echo $DATABASE_URL
echo $REDIS_URL
echo $PORT
```

---

## 2. Deployment Steps

Render uses **GitHub webhooks** for continuous deployment. No manual build step is needed.

### Automatic Deploy Flow

```
git push origin main
       │
       ▼
GitHub webhook fires ──▶ Render detects push
       │
       ▼
Render builds from backend/Dockerfile
  • pip install --no-cache-dir -r requirements.txt
  • COPY application code
       │
       ▼
Render starts new instance
  • CMD: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       │
       ▼
Health check passes ──▶ Traffic shifts to new instance (zero-downtime)
```

### Manual Deploy (if needed)

1. Go to **Render Dashboard → Your Service → Manual Deploy**.
2. Select the commit or branch to deploy.
3. Click **Deploy**.

### First-Time Setup

1. Create a new **Web Service** in the Render dashboard.
2. Connect the GitHub repository (`SupplyChain.AI`).
3. Set **Root Directory** to `backend`.
4. Set **Environment** to `Docker`.
5. Configure the environment variables from Section 1.
6. Deploy.

---

## 3. Health Verification

After every deployment, verify the service is live before declaring success.

### Automated (Render Health Check)

Configure in Render Dashboard → Health Check:

- **Path:** `/health`
- **Timeout:** 5 seconds
- **Interval:** 10 seconds

Render will not shift traffic to a new instance until `/health` returns HTTP 200.

### Manual Verification

```bash
# Quick liveness check
curl -s https://your-service.onrender.com/health | jq .

# Expected response:
# {
#   "status": "ok",
#   "service": "SupplyChainAI Backend",
#   "uptime_s": 12.3
# }
```

### Extended Checks

```bash
# API endpoints reachable
curl -s https://your-service.onrender.com/api/scenarios | jq '.[0].id'
# Expected: "kaohsiung_typhoon"

# WebSocket stream connectable
websocat ws://your-service.onrender.com/ws/simulation
# Send: {"beta": 0.6, "market_adoption_pct": 0.0, "shock_intensity": 0.85}
# Expect: streaming JSON frames at ~30 fps

# OpenAPI docs accessible
curl -s -o /dev/null -w "%{http_code}" https://your-service.onrender.com/docs
# Expected: 200
```

---

## 4. Emergency Rollback

Use this procedure when a deployment causes failures — API errors, WebSocket stream crashes under load, or health check failures.

### Option A: Rollback via Render Dashboard (fastest)

1. Go to **Render Dashboard → Your Service → Events**.
2. Find the **last successful deploy**.
3. Click **Redeploy** on that event.
4. Verify via `/health` (Section 3).

### Option B: Rollback via Git Revert

```bash
# 1. Identify the last known-good commit
git log --oneline -10

# 2. Revert the bad commit(s)
git revert HEAD --no-edit

# 3. Push to main — Render auto-deploys the revert
git push origin main

# 4. Verify health
curl -s https://your-service.onrender.com/health | jq .
```

### Option C: Hard Reset (nuclear option — use only if revert is complex)

```bash
# 1. Reset main to the last known-good commit
git reset --hard <good-commit-sha>

# 2. Force push (⚠️ destructive — coordinate with team first)
git push origin main --force

# 3. Verify health
curl -s https://your-service.onrender.com/health | jq .
```

### Post-Incident

1. Confirm `/health` returns `{"status": "ok"}`.
2. Spot-check `/api/scenarios` and `/api/manifold/frame`.
3. Test WebSocket connectivity to `/ws/simulation`.
4. Notify the team in Slack/Discord with a brief summary of what went wrong and what was rolled back.
