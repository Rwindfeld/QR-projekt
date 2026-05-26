"""
Build grafana/dashboard-public.json — no template variables (required for public sharing).
Set GRAFANA_POSTGRES_UID to your Postgres datasource UID in Grafana Cloud (Connections).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "grafana" / "dashboard.json"
OUT = ROOT / "grafana" / "dashboard-public.json"

# Set this to match your Grafana Postgres datasource UID (Connections → PostgreSQL → UID in URL/settings)
POSTGRES_UID = os.environ.get("GRAFANA_POSTGRES_UID", "grafanacloud-postgres-qr")

MAX_LAV_SCANS = 5


def main() -> None:
    dash = json.loads(SRC.read_text(encoding="utf-8"))
    text = json.dumps(dash, ensure_ascii=False)

    text = text.replace("${DS_POSTGRES}", POSTGRES_UID)
    text = text.replace("${DS_PROMETHEUS}", POSTGRES_UID)  # drop prom panels below
    text = text.replace("${max_lav_scans}", str(MAX_LAV_SCANS))
    text = text.replace("≤ ${max_lav_scans}", f"≤ {MAX_LAV_SCANS}")
    text = text.replace("(0–${max_lav_scans} scanninger)", f"(0–{MAX_LAV_SCANS} scanninger)")

    dash = json.loads(text)
    dash["templating"] = {"list": []}
    dash["title"] = "QR Spilcafé — offentlig visning"
    dash["uid"] = "qr-cafe-public"
    dash["version"] = 1
    dash["description"] = (
        "Public dashboard — ingen template-variabler. "
        "Importer og vælg Postgres-datasource med UID: " + POSTGRES_UID
    )

    # Prometheus panels virker sjældent i public view uden ekstra opsætning
    dash["panels"] = [p for p in dash["panels"] if p.get("datasource", {}).get("type") != "prometheus"]

    # Fjern panel-links der kræver login
    for panel in dash["panels"]:
        fc = panel.get("fieldConfig", {}).get("defaults", {})
        if "links" in fc:
            del fc["links"]
        for ov in panel.get("fieldConfig", {}).get("overrides", []):
            for prop in ov.get("properties", []):
                if prop.get("id") == "links":
                    prop["value"] = []

    # Opdater intro-tekst
    for panel in dash["panels"]:
        if panel.get("id") == 100:
            panel["options"]["content"] = (
                "**Offentlig visning — efterspørgsel ved hylden**\n\n"
                "Data opdateres automatisk hvert 30. sek. "
                f"Spil med ≤ {MAX_LAV_SCANS} scanninger overvejes til udskiftning."
            )

    OUT.write_text(json.dumps(dash, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK -> {OUT} (Postgres UID: {POSTGRES_UID}, {len(dash['panels'])} panels)")


if __name__ == "__main__":
    main()
