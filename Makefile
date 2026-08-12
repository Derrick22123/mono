.PHONY: install dev build test lint serve health api web

install:
	cd apps/api && uv sync --extra dev
	cd apps/web && pnpm install

dev:
	@echo "Run in two terminals: make api && make web"
	@$(MAKE) api

api:
	cd apps/api && uv run uvicorn app.main:app --app-dir src --host 0.0.0.0 --port $${AGENT_OS_PORT:-7777} --reload

web:
	cd apps/web && pnpm dev

build:
	cd apps/web && pnpm build
	cd apps/api && uv sync --extra dev

test:
	cd apps/api && uv run pytest

lint:
	cd apps/api && uv run ruff check src tests && uv run ruff format --check src tests
	cd apps/web && pnpm lint

serve:
	@test -d apps/web/dist || (echo "Run make build first" && exit 1)
	cd apps/api && uv run uvicorn app.main:app --app-dir src --host 0.0.0.0 --port $${AGENT_OS_PORT:-7777}

health:
	@curl -sf "http://localhost:$${AGENT_OS_PORT:-7777}/v1/health" | python3 -m json.tool
