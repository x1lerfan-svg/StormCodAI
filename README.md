# StormCodAI

StormCodAI is a security-conscious AI coding workspace and coding-agent foundation.

## Current status

**v0.1.1 — Secure app foundation**

StormCodAI now has a professional web shell and a local server/API boundary. The browser never receives the model provider key. The current agent remains proposal-only: it can inspect the bounded workspace and return guidance, but it cannot execute arbitrary shell commands or automatically apply model-generated edits.

## Run the app

Configure the model:

```bash
export STORMCODAI_API_KEY="your-key"
export STORMCODAI_BASE_URL="https://api.openai.com/v1"
export STORMCODAI_MODEL="your-model"
```

Start the application:

```bash
python -m stormcodai serve
```

Open `http://127.0.0.1:8080`.

Optional environment variables:

```text
STORMCODAI_HOST=127.0.0.1
STORMCODAI_PORT=8080
STORMCODAI_WORKSPACE=stormcodai_workspace
```

## API

- `GET /api/health` — health check
- `GET /api/status` — runtime mode and capability boundary
- `GET /api/workspace` — bounded workspace inventory and limits
- `GET /api/tools` — explicitly available tools
- `POST /api/chat` — validated coding request

The API enforces a 64 KiB JSON body limit, 4,000-character prompt limit, basic per-client rate limiting, generic provider errors, and safe static-file path handling.

## Python CLI

```bash
python -m stormcodai
```

## Development

```bash
python -m unittest discover -s tests -v
```

## Security

See [docs/APP_ARCHITECTURE.md](docs/APP_ARCHITECTURE.md).

Never commit API keys, tokens, passwords, private keys or `.env` files. For GitHub integration, the planned production design uses a GitHub App with minimum repository permissions and short-lived installation tokens.

## Roadmap

1. Secure app/API foundation — current.
2. Streaming agent events.
3. Patch/diff engine with approval and atomic apply.
4. Isolated test/command sandbox.
5. GitHub App integration.
6. Authentication, projects and audit logs.
7. Production deployment and observability.
