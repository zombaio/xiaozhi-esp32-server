# Copilot instructions for xiaozhi-esp32-server

Purpose: help an AI coding agent get productive quickly in this repository by highlighting architecture, run/debug workflows, important conventions, and integration points.

- **Big picture (quick):**
  - The core runtime is the Python service in `main/xiaozhi-server` — an asyncio-based server that runs a WebSocket service (voice/device transport) and a small HTTP server (OTA / vision endpoints). Entry: `main/xiaozhi-server/app.py`.
  - Admin UI is in `main/manager-web` (Vue CLI). Backend admin API is `main/manager-api` (Spring Boot). These are orchestrated for full deployments via `main/xiaozhi-server/docker-compose_all.yml`.
  - Persistence: MySQL + Redis in `docker-compose_all.yml`. Models and large files are mounted at runtime from `./models` and `./data`.

- **Key runtime facts / invariants to respect:**
  - Config layering: `data/.config.yaml` (developer overrides) takes precedence over `main/xiaozhi-server/config.yaml`. Do not edit `config.yaml` for secrets—use `data/.config.yaml`.
  - `auth_key` precedence: value in `server.auth_key` → `manager-api.secret` → generated UUID (see `app.py`). AI agents should avoid hard-coding credentials.
  - MCP endpoint format: expected websocket style `/mcp/`; `app.py` normalizes to `/call/` for outgoing calls. Validate `mcp_endpoint` format before changing code.
  - Default ports: websocket 8000, HTTP 8003 (see `config.yaml` and `app.py`). Docker binds these ports in `docker-compose_all.yml`.

- **How to run & debug locally (examples):**
  - Run Python server directly (dev):
    - cd `main/xiaozhi-server` and run `python app.py` (prefer a venv with requirements from `main/xiaozhi-server/requirements.txt`).
  - Full docker-compose (recommended for integration):
    - from repo root: `docker-compose -f main/xiaozhi-server/docker-compose_all.yml up --build`
    - Note: model files are mounted from `./models/...` and config overrides from `./data/.config.yaml`.
  - Admin UI (manager-web):
    - `cd main/manager-web` then `pnpm install` (or `npm install`) and `pnpm run serve` (scripts are in `main/manager-web/package.json`). Backend API (manager-api) is a Spring Boot app — see `main/manager-api/README.md` for build and run.

- **Project-specific patterns & conventions**
  - Config is centralized and environment-agnostic: prefer `data/.config.yaml` overrides. Search for `load_config()` usage (in `main/xiaozhi-server/config`) when changing config behavior.
  - Long-running tasks use asyncio tasks and explicit cancellation in `app.py` — when modifying services, ensure graceful shutdown: cancel tasks and await with timeout (see existing pattern in `main/xiaozhi-server/app.py`).
  - Binary/tool checks at startup: e.g., ffmpeg presence is validated on launch (`check_ffmpeg_installed()`), so any container or developer environment must include required native dependencies.
  - Logs and data dirs: default `data_dir` is `data` and log dir `tmp` (configured in `config.yaml`). Avoid changing paths without updating docker mounts.

- **Integration points & external dependencies**
  - Model files (TTS/STT/ASR models) are expected to be mounted and may be large — see `docker-compose_all.yml` volume mounts.
  - `mcp_endpoint` connects to an external MCP gateway (websocket). Related docs: `docs/mcp-endpoint-integration.md`.
  - Plugins call external APIs (weather, news, ragflow). Check `config.yaml` plugin sections for host and token patterns.

- **When changing code, check these files first:**
  - `main/xiaozhi-server/app.py` — service lifecycle and ports
  - `main/xiaozhi-server/config.yaml` and `data/.config.yaml` — configuration precedence
  - `main/xiaozhi-server/docker-compose_all.yml` — deployment mounts, ports, and healthchecks
  - `main/manager-web/package.json` and `main/manager-api/README.md` — admin UI and API run/build steps

- **Concrete examples to copy/paste**
  - Start server locally: `cd main/xiaozhi-server && python app.py`
  - Start full stack: `docker-compose -f main/xiaozhi-server/docker-compose_all.yml up -d --build`

- **Do not assume / avoid**
  - Do not hard-code secrets into `config.yaml`; use `data/.config.yaml` or manager-api settings.
  - Do not remove the task cancellation / wait logic in `app.py` — it prevents hanging shutdowns.

If anything above is unclear or you want more examples (launch configs, common PR templates, or test commands), tell me which area to expand.
