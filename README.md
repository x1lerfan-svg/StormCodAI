# StormCodAI

StormCodAI is a security-conscious AI coding workspace and coding-agent foundation.

## Current status

**v0.1.0 — Foundation + professional app shell**

The Python core inspects a bounded local workspace and asks an OpenAI-compatible model for coding guidance. It is proposal-only: no model-generated file edits or arbitrary command execution.

A dependency-free web app shell is available in `web/`. It is a presentation layer; secrets and privileged operations remain server-side.

## Web app

Run locally with Python:

```bash
python -m http.server 8080 --directory web
```

Open `http://127.0.0.1:8080`.

The UI is not directly connected to the model yet. The next milestone is a server-side API with validated, streamed agent events.

## Python agent

```bash
python -m stormcodai
```

Environment:

```text
STORMCODAI_API_KEY=
STORMCODAI_BASE_URL=https://api.openai.com/v1
STORMCODAI_MODEL=
```

Never commit API keys, tokens, passwords or `.env` files.

## Development

```bash
python -m unittest discover -s tests -v
```

See [docs/APP_ARCHITECTURE.md](docs/APP_ARCHITECTURE.md) for the security boundaries and roadmap.