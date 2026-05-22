# Grafana Cloud — datakilder til QR-prototypen

Stack: [https://rfwjensen.grafana.net](https://rfwjensen.grafana.net)  
Region: `prod-eu-west-2` (EU Germany)

## 1. Postgres (applikationsdata: scans, top spil)

Grafana Cloud kan ikke nå din lokale Postgres direkte. Vælg **én** metode til demoen:

### A) Hurtigste til demo: Cloudflare Tunnel

1. Installer [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/).
2. Start tunnel (erstatter ikke din firewall permanent — kun mens du demoer):

```bash
cloudflared tunnel --url tcp://localhost:5432
```

3. Cloudflared viser en offentlig proxy-URL. I Grafana Cloud → **Connections** → **Data sources** → **Add data source** → **PostgreSQL**:
   - **Host**: værdien fra cloudflared (host + port)
   - **Database**: `QR`
   - **User** / **Password**: `postgres` / `1590`
   - **TLS/SSL**: Mode *require* eller *disable* afhængigt af tunnel-output (test med **Save & test**)
4. Gem datakilden som f.eks. `QR-Postgres-Local`.

> Luk tunnelen når demoen er slut — din database må ikke stå åbent unødigt.

### B) Mere “produktion”: Private Data Source Connect (PDC)

Til skoleprojektets “rigtige” arkitektur-notat:

- API endpoint: `pdc-grafana-datasources-api.eu-central-1.vpce.grafana.net`
- SSH endpoint: `pdc-grafana-datasources.eu-central-1.vpce.grafana.net`

Følg officiel guide:  
[Private Data Source Connect](https://grafana.com/docs/grafana-cloud/connect-externally-hosted/private-data-source-connect/)

Opsummering:

1. Grafana Cloud → din stack → **Connections** → **Private data source connect** → opret network + agent.
2. Kør PDC-agenten på samme maskine som Docker (peger på `localhost:5432`).
3. Opret Postgres data source i UI med PDC-netværket valgt.

## 2. Prometheus (infrastruktur + app-metrics via Alloy)

Din stack har allerede en managed Prometheus-instans (typisk navngivet `grafanacloud-rfwjensen-prom`).

1. **Alloy** i `docker-compose.yml` remote-writer med:
   - URL: `GRAFANA_CLOUD_PROM_URL` (fra `.env`)
   - Bruger: `GRAFANA_CLOUD_PROM_USER` (numerisk instance ID)
   - Password: `GRAFANA_ALLOY_TOKEN`
2. I Grafana → **Explore** → vælg Prometheus → kør:

```promql
{stack="qr-projekt"}
```

3. Hvis du ser metrics, er Prometheus datakilden klar til dashboard-import.

### Find `GRAFANA_CLOUD_PROM_USER`

1. Log ind på [Grafana Cloud Portal](https://grafana.com/).
2. **My Account** → vælg stack **rfwjensen**.
3. Under **Prometheus** / **Metrics** findes **Instance ID** (kun tal) — det er `GRAFANA_CLOUD_PROM_USER`.
4. **Access Policies** → token med `metrics:write` → det er `GRAFANA_ALLOY_TOKEN`.

## 3. Import af dashboard

1. **Dashboards** → **New** → **Import**.
2. Upload `grafana/dashboard.json`.
3. Map **Postgres** og **Prometheus** til dine datakilder ved import-prompten.
4. Gem — refresh 30s er forudindstillet.
