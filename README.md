# QR Spilcafé — Game Tracking Prototype (v2)

Prototype til skoleprojekt (LCA: QR vs RFID). Gæster scanner QR → data i **PostgreSQL** (via **PgBouncer**) → Grafana Cloud. Metrics pushes af **Grafana Alloy** (lokalt, uden Docker).

## Forudsætninger (lokalt)

- **PostgreSQL 16** på `localhost:5432`
- **PgBouncer** på `localhost:6432` → peger på database `QR`
- **Python 3.11+**
- **Grafana Alloy** (valgfrit til metrics): `winget install GrafanaLabs.Alloy`
- `.env` med Grafana Cloud credentials (se `.env.example`)

## Hurtig start

### 1. Database (én gang)

I **pgAdmin** på server `localhost:5432`:

1. Kør `pgadmin-setup.sql` hvis databasen `QR` ikke findes.
2. Forbind til database **QR** → Query Tool → kør `schema.sql`, derefter `seed.sql`.

Merge også `pgbouncer/pgbouncer.ini` + `userlist.txt` i din eksisterende PgBouncer, hvis stats-brugeren mangler.

### 2. Miljø

```powershell
cd "c:\Users\windf\OneDrive\Documents\QR"
# .env skal allerede være udfyldt (GRAFANA_* + DATABASE_URL)
```

### 3. Start app (terminal 1)

```powershell
.\start.cmd
```

*(Hvis `.\start.ps1` fejler med "scripts is disabled", brug altid `.cmd` i stedet.)*

### 4. Start Alloy (terminal 2)

```powershell
.\start-alloy.cmd
```

### 5. Test

| URL | Formål |
|-----|--------|
| http://localhost:8000/healthz | App OK |
| http://localhost:8000/scan/catan | Tak-side + log scan |
| http://localhost:8000/admin/qrcodes | Print QR-ark |
| http://localhost:8000/metrics | Prometheus metrics |

Verificér Grafana Cloud → Explore → `{stack="qr-projekt"}`.

## PowerShell-scripts

| Script | Handling |
|--------|----------|
| `.\start.cmd` | App (venv + uvicorn) |
| `.\start-alloy.cmd` | Alloy → Grafana Cloud |
| `.\verify.cmd` | Tjek healthz + metrics |
| `.\scripts\seed-local.ps1` | Kør `seed.sql` igen (kræver `psql`) |

## Konfiguration (`.env`)

| Variabel | Beskrivelse |
|----------|-------------|
| `DATABASE_URL` | `postgresql://postgres:1590@localhost:6432/QR` (via PgBouncer) |
| `GRAFANA_ALLOY_TOKEN` | Access policy token |
| `GRAFANA_CLOUD_PROM_URL` | Din push-URL fra Grafana (fx `...prod-65-prod-eu-west-2...`) |
| `GRAFANA_CLOUD_PROM_USER` | Instance ID (fx `3222300`) |

## Stack

| Komponent | Port |
|-----------|------|
| PostgreSQL | 5432 |
| PgBouncer | 6432 |
| FastAPI | 8000 |
| Alloy (debug UI) | 12345 |

Alloy-config: `alloy/config.local.alloy` (localhost).  
`alloy/config.alloy` er kun til Docker — **bruges ikke** i lokal opsætning.

## Grafana Cloud

1. **Prometheus** — Alloy pusher med `stack="qr-projekt"`.
2. **Postgres** — [grafana/datasources.md](grafana/datasources.md) (cloudflared tunnel til demo).
3. **Dashboard** — import `grafana/dashboard.json`.

### Postgres-tunnel (demo)

```powershell
cloudflared tunnel --url tcp://localhost:5432
```

## pgAdmin

- Server: `localhost:5432`, bruger `postgres`, password `1590`
- App bruger **6432** (PgBouncer); pgAdmin kan bruge 5432 direkte

## LCA (QR vs RFID)

- **Hardware**: QR = papir/plastik; RFID = tags + læsere
- **Energi**: QR bruger gæstens telefon; RFID-læsere kører kontinuerligt
- **Affald**: QR billigt at udskifte; RFID giver e-waste

## Fejlsøgning

| Problem | Løsning |
|---------|---------|
| `relation "games" does not exist` | Kør `schema.sql` + `seed.sql` i pgAdmin |
| PgBouncer auth fejl | Tjek `pgbouncer/userlist.txt` mod passwords i `.env` |
| Alloy pusher ikke | Tjek `.env`, kør `start-alloy.ps1`, se Explore efter 1–2 min |
| Port 8000 optaget | Stop anden uvicorn eller skift port i script |
| `scripts is disabled` | Brug `start.cmd` / `start-alloy.cmd` (ikke `.ps1`) |
| Tomme Grafana SQL-paneler | Postgres data source / cloudflared tunnel |

## Permanent URL til trykte QR-koder (Render)

Print QR med **Render** — fast `https://qr-spilcafe.onrender.com` (ændres ikke).  
Følg **[DEPLOY.md](DEPLOY.md)** (GitHub → Render Blueprint → `/admin/qrcodes` → print).

## Sikkerhed

- Token kun i `.env` (gitignored)
- Rotér token hvis den er lækket

## Valgfri: Docker

`docker-compose.yml` findes til reference, men er **ikke nødvendig** for dette projekt.
