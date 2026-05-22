# Valgfrit — kun hvis du bruger Docker. Lokal kørsel: .\start.ps1 (se README.md)
.PHONY: up down logs logs-alloy qr seed psql verify

up:
	@echo "Docker er valgfrit. Brug i stedet: .\\start.ps1 og .\\scripts\\start-alloy.ps1"
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

logs-alloy:
	docker compose logs -f alloy

qr:
	curl -s http://localhost:8000/admin/qrcodes > /dev/null
	@echo "QR codes regenerated in ./qrcodes/"

seed:
	docker compose exec -T postgres psql -U postgres -d QR -f - < seed.sql
	@echo "seed.sql applied"

psql:
	docker compose exec postgres psql -U postgres -d QR

verify:
	@echo "=== /healthz ==="
	curl -sf http://localhost:8000/healthz || (echo "FAIL healthz" && exit 1)
	@echo ""
	@echo "=== /metrics (first 5 lines) ==="
	curl -sf http://localhost:8000/metrics | head -n 5
	@echo ""
	@echo "=== Alloy healthy ==="
	curl -sf http://localhost:12345/-/healthy 2>/dev/null || docker compose exec alloy wget -q -O- http://127.0.0.1:12345/-/healthy
	@echo ""
	@echo "OK — check Grafana Cloud → Explore for recent metrics (stack=qr-projekt)"
