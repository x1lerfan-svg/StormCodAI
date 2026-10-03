# StormCodAI

StormCodAI is a lightweight AI coding agent.

## MVP
- Chat with an AI coding model
- Read project files
- Propose file changes
- Apply safe file changes inside a workspace
- Keep model access configurable through an OpenAI-compatible HTTP API

## Run

```bash
python -m stormcodai
```

Set these environment variables:

```text
STORMCODAI_API_KEY=your-key
STORMCODAI_BASE_URL=https://api.openai.com/v1
STORMCODAI_MODEL=your-model
```

The first version intentionally uses Python's standard library for the model client.
