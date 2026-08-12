# mono

Agent Chat App monorepo — Agno AgentOS backend + assistant-ui frontend.

## Quick start

See [specs/001-agent-chat-app/quickstart.md](specs/001-agent-chat-app/quickstart.md) for end-to-end validation scenarios.

```bash
make install
export OPENAI_API_KEY=sk-...          # or DEEPSEEK_API_KEY
export OPENAI_BASE_URL=https://api.deepseek.com   # optional; this is the default
export OPENAI_MODEL=deepseek-v4-flash             # or deepseek-v4-pro
export VITE_API_BASE_URL=http://localhost:7777
make dev   # run `make api` and `make web` in separate terminals
```

## Makefile commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python (uv) and web (pnpm) dependencies |
| `make api` | Start Agno AgentOS on port 7777 (default) |
| `make web` | Start Vite dev server for `apps/web` |
| `make build` | Build web SPA to `apps/web/dist` |
| `make serve` | Serve API + built SPA from one process |
| `make health` | `curl` the `/v1/health` readiness endpoint |
| `make test` | Run backend pytest suite |
| `make lint` | Run Ruff (api) and ESLint (web) |

## Layout

- `apps/api` — FastAPI / Agno AgentOS (`POST /agui`, `GET /v1/health`)
- `apps/web` — Vite + React + assistant-ui (繁體中文 UI)
- `specs/001-agent-chat-app/` — feature spec, plan, contracts, tasks

Copy `.env.example` to configure local environment variables.
