# Deploy til Render (permanent URL til trykte QR-koder)

Efter deploy får du en **fast adresse** som:

```text
https://qr-cafe.onrender.com
```

Den ændres ikke. Print QR **én gang** efter deploy.

---

## 1. GitHub-repo

I PowerShell:

```powershell
cd "c:\Users\windf\OneDrive\Documents\QR"
git init
git add .
git commit -m "QR café prototype — Render deploy"
```

Opret et **privat** repo på GitHub (uden `.env` — den er i `.gitignore`).

```powershell
git remote add origin https://github.com/Rwindfeld/QR-projekt.git
git branch -M main
git push -u origin main
```

---

## 2. Render Blueprint

1. Gå til [https://dashboard.render.com](https://dashboard.render.com) og log ind (gratis).
2. **New** → **Blueprint**.
3. Forbind GitHub og vælg dit `qr-cafe` repo.
4. Render læser `render.yaml` og opretter:
   - **qr-db** (PostgreSQL, gratis)
   - **qr-cafe** (web service, gratis)
5. Klik **Apply** og vent på deploy (5–10 min første gang).

---

## 3. Grafana-miljøvariabler på Render

Når web servicen er oppe: **qr-cafe** → **Environment** → tilføj (fra din lokale `.env`):

| Key | Value |
|-----|--------|
| `GRAFANA_ALLOY_TOKEN` | din `glc_…` token |
| `GRAFANA_CLOUD_PROM_URL` | din Prometheus push URL |
| `GRAFANA_CLOUD_PROM_USER` | `3222300` |

**Sæt ikke `BASE_URL` manuelt** — app bruger `RENDER_EXTERNAL_URL` automatisk.

Klik **Save** → ny deploy.

---

## 4. Test den permanente URL

Din URL står under **qr-cafe** → øverst (fx `https://qr-cafe-xxxx.onrender.com`).

Test i mobilbrowser på **4G** (ikke kun Wi‑Fi):

```text
https://DIN-RENDER-URL.onrender.com/healthz
https://DIN-RENDER-URL.onrender.com/scan/catan
```

Første request efter idle kan tage ~30 sek (gratis tier).

---

## 5. Generér QR til print (én gang)

Åbn i browser:

```text
https://DIN-RENDER-URL.onrender.com/admin/qrcodes
```

Højreklik → gem billeder, eller print siden.  
Alle QR peger nu på den **permanente** Render-URL.

Opdater evt. `BASE_URL` lokalt i `.env` til samme URL — kun til lokal test af PNG-generering.

---

## 6. Grafana Cloud efter Render

**Prometheus (app-metrics):** Kør Alloy lokalt med `alloy/config.render.alloy` — scraper din Render `/metrics` og pusher til Cloud.

```powershell
set RENDER_APP_URL=https://DIN-RENDER-URL.onrender.com
.\scripts\start-alloy-render.cmd
```

**Postgres (SQL-paneler):** I Grafana Cloud → Postgres data source → brug **External connection string** fra Render (**qr-db** → **Connections**). SSL: require.

---

## 7. Omdøb service (valgfrit)

I Render → **qr-cafe** → **Settings** → **Name** → fx `qr-spilcafe` giver URL:

`https://qr-spilcafe.onrender.com`

Gør dette **før** du printer QR, hvis du vil have et pænt navn.

---

## Fejlsøgning

| Problem | Løsning |
|---------|---------|
| Deploy fejler | **Logs** → build; tjek `requirements.txt` |
| 500 på /scan | **Logs** → startup; app kører `bootstrap()` automatisk (gratis tier har ikke preDeploy) |
| Database | **qr-db** skal være **Available** og linket til web service |
| Cold start | Normal på gratis plan — vent 30 sek |

---

## Lokal vs Render

| | Lokal (`start.cmd`) | Render |
|--|---------------------|--------|
| URL | localhost | Permanent HTTPS |
| QR print | Kun test | **Brug dette til spil** |
| PC tændt | Ja | Nej |
