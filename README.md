# StormCodAI

StormCodAI is a lightweight, security-conscious AI coding agent.

## Current status

Version 0.1.0 is the foundation release. The agent can inspect a bounded local workspace and ask a configurable OpenAI-compatible model for coding guidance. It is proposal-only: it does not yet apply model-generated edits or execute arbitrary commands.

## Design goals

- Small, auditable core
- Safe workspace boundary
- Configurable model-provider abstraction
- Tests and CI before autonomous write/execute capabilities
- Explicit approval gates for destructive operations

## Run

    python -m stormcodai

Configure the model through environment variables:

    STORMCODAI_API_KEY=your-key
    STORMCODAI_BASE_URL=https://api.openai.com/v1
    STORMCODAI_MODEL=your-model

Do not commit API keys, tokens, passwords, or .env files. GitHub provides secret scanning and push protection for preventing accidental credential exposure.

## Development

Run the test suite with:

    python -m unittest discover -s tests -v

GitHub Actions will run tests on pushes and pull requests. Workflows belong in .github/workflows.
