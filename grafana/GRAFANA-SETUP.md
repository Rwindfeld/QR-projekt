# Grafana Cloud — opsætning med Render (qr-spilcafe)

Stack: **[rfwjensen.grafana.net](https://rfwjensen.grafana.net)**

Du skal have **to datakilder** + **import af dashboard**.

---

## Del 1: Postgres (scanninger, top spil, tabeller)

Din database ligger på Render (`qr-db`), ikke på din pc.

### Trin 1 — Hent forbindelsesdata fra Render

1. Gå til [dashboard.render.com](https://dashboard.render.com)
2. Klik **qr-db** (PostgreSQL)
3. Fanen **Connections** eller **Info**
4. Kopiér **External Database URL** (starter med `postgresql://...`)

Den ligner fx:

```text
postgresql://qr:XXXX@dpg-xxxxx-a.frankfurt-postgres.render.com/qr
```

> Gem URL i din lokale `.env` som `RENDER_DATABASE_URL` (valgfrit, til test).

### Trin 2 — Opret Postgres i Grafana Cloud

1. Åbn **[rfwjensen.grafana.net](https://rfwjensen.grafana.net)**
2. **Connections** (menu) → **Add new connection** → **PostgreSQL**
3. Udfyld (fra URL'en ovenfor):

| Felt | Værdi |
|------|--------|
| **Name** | `QR-Render-Postgres` |
| **Host** | `dpg-xxxxx-a.frankfurt-postgres.render.com` |
| **Port** | `5432` |
| **Database** | `qr` |
| **User** | `qr` |
| **Password** | (password fra Render — vises ved URL) |
| **TLS/SSL Mode** | `require` |
| **Version** | 16 |

4. Klik **Save & test** → skal vise **green OK**

### Fejlsøgning Postgres

| Fejl | Løsning |
|------|---------|
| Connection refused | Tjek at du bruger **External** URL, ikke Internal |
| SSL required | Sæt TLS til **require** |
| Auth failed | Kopiér password igen fra Render (ingen mellemrum) |
| Test OK men tomme paneler | Kør 2–3 scans på `/scan/catan` først |

### Test-query i Grafana

**Explore** → vælg `QR-Render-Postgres` → SQL:

```sql
SELECT g.name, COUNT(*) AS scans
FROM scans s
JOIN games g ON g.id = s.game_id
GROUP BY g.name
ORDER BY scans DESC;
```

Du bør se Catan, Azul osv.

---

## Del 2: Prometheus (scan-rate, latency)

Metrics kommer fra din **Render-app**, ikke fra lokal pc.

### Trin 1 — Start Alloy på din Windows-pc

Alloy scraper `https://qr-spilcafe.onrender.com/metrics` og pusher til Grafana Cloud.

1. Tjek at `.env` har (fra din Grafana Cloud portal):

   - `GRAFANA_ALLOY_TOKEN`
   - `GRAFANA_CLOUD_PROM_URL`
   - `GRAFANA_CLOUD_PROM_USER` (= `3222300`)

2. I **PowerShell** (ny terminal):

```powershell
cd "c:\Users\windf\OneDrive\Documents\QR"
set RENDER_APP_URL=https://qr-spilcafe.onrender.com
.\scripts\start-alloy-render.cmd
```

Lad vinduet stå åbent mens du vil have metrics (til demo/plakat).

### Trin 2 — Verificér metrics

1. Grafana → **Explore**
2. Data source: **grafanacloud-rfwjensen-prom** (eller din Prometheus)
3. Query:

```promql
{stack="qr-projekt"}
```

4. Lav et par scans: https://qr-spilcafe.onrender.com/scan/azul

Efter 1–2 min: se `scans_total`, `http_request_duration_seconds_*`.

---

## Del 3: Import dashboard

1. Grafana → **Dashboards** → **New** → **Import**
2. **Upload** filen `grafana/dashboard.json` fra projektet
3. Ved import-mapping:
   - **Postgres** → `QR-Render-Postgres`
   - **Prometheus** → `grafanacloud-rfwjensen-prom`
4. Klik **Import**

Dashboardet har 12 paneler (8 SQL + 4 Prometheus), danske titler, 30s refresh.

### Screenshots til A1-plakat

Anbefalede paneler:

- Scanninger i dag / denne uge
- Top 10 spil denne uge
- Scanninger pr. dag (30 dage)
- App scan-rate (Prometheus)

---

## Testdata (6 måneders scanninger)

Kør lokalt mod Render-databasen (sæt `RENDER_DATABASE_URL` i `.env`):

```powershell
cd "c:\Users\windf\OneDrive\Documents\QR"
.\scripts\generate-test-scans.cmd
```

Eller med custom antal:

```powershell
.\.venv\Scripts\python.exe scripts\generate_test_scans.py --months 6 --count 2000
```

Tilføjer **kun** nye rækker — sletter ikke dine rigtige scans. I Grafana: vælg **Last 6 months**.

---

## Del 4: Del dashboard offentligt (med live data)

Grafana viser **"Template variables are not supported"** — brug derfor **`dashboard-public.json`**, ikke `dashboard.json`.

**Du behøver ikke finde UID.** Ved import vælger du Postgres-datakilden i en dropdown.

### Trin 1 — Tjek at Postgres virker

1. [rfwjensen.grafana.net](https://rfwjensen.grafana.net) → **Explore**
2. Datakilde: din Postgres (`grafanacloud-postgres-datasource` eller lign.)
3. Kør:

```sql
SELECT COUNT(*) FROM scans;
```

→ Skal vise et tal **større end 0**. Hvis 0: lav et par scans på https://qr-spilcafe.onrender.com/scan/catan

### Trin 2 — Importér public-dashboard

1. **Dashboards** (venstre menu) → **New** → **Import**
2. **Upload JSON file** → vælg `grafana/dashboard-public.json` fra projektmappen  
   (eller fra GitHub: repo → `grafana/dashboard-public.json` → Download)
3. Grafana spørger om **datakilde-mapping** — vælg din **Postgres** (den med Render-host `dpg-...oregon-postgres.render.com`)
4. Klik **Import**

### Trin 3 — Tjek dashboardet (logget ind)

1. Åbn dashboardet **"QR Spilcafé — offentlig visning"**
2. Øverst til højre: tidsinterval **Last 180 days** (eller 6 months)
3. Refresh: **30s** (ikke **Off**)
4. Paneler skal vise tal og tabeller — **ikke** "No data"

Hvis stadig "No data": klik et panel → **Edit** → under **Query** tjek at datakilde er din Postgres → **Apply** → **Save dashboard**.

### Trin 4 — Opret offentligt link

1. På dashboardet: **Share** (ikon øverst) → **Public dashboard** / **Share externally**
2. **Enable** (slå deling til)
3. Slå **Enable time range** til
4. **Copy external link**
5. Åbn linket i **privat/incognito** — data skal vises

**Brug ikke** public link fra det gamle dashboard (med variabler). **Revoke** gammelt link hvis det stadig er aktivt.

### Kun hvis import fejler (sjældent): find UID

UID står i **browserens adresselinje**, når du er på Postgres-indstillinger:

```text
.../connections/datasources/edit/HER-ER-UID
```

Kopiér teksten efter `/edit/`. Regenerér JSON:

```powershell
cd "c:\Users\windf\OneDrive\Documents\QR"
$env:GRAFANA_POSTGRES_UID="UID-fra-URL"
.\.venv\Scripts\python.exe scripts\build_public_dashboard.py
```

Importér `dashboard-public.json` igen.

---

## Hurtig checklist

- [ ] Render **qr-db** → External URL kopieret
- [ ] Grafana Postgres **Save & test** = OK
- [ ] Alloy kører med `RENDER_APP_URL`
- [ ] Explore: `{stack="qr-projekt"}` viser data
- [ ] `dashboard.json` importeret med rigtige datakilder
- [ ] Mindst 5 test-scans lavet

---

## Arkitektur (til rapport/plakat)

```text
Gæst (QR) → qr-spilcafe.onrender.com → Render Postgres
                    ↓
              /metrics ← Alloy (din pc) → Grafana Cloud Prometheus
Render Postgres ────────────────────────→ Grafana Cloud (SQL-paneler)
```

---

## Filer i projektet

| Fil | Indhold |
|-----|---------|
| `grafana/dashboard.json` | Privat dashboard (med variabler) |
| `grafana/dashboard-public.json` | **Offentlig deling** — ingen variabler |
| `grafana/queries.sql` | SQL til paneler (reference) |
| `grafana/queries.promql` | PromQL (reference) |
| `alloy/config.render.alloy` | Alloy mod Render |

Mere baggrund: [datasources.md](datasources.md)
