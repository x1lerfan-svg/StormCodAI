# StormCodAI App Architecture

StormCodAI is evolving from a coding-agent core into a professional AI coding workspace.

## Trust boundaries

User -> Web UI -> Server API -> Agent -> Policy -> Tool -> Result -> Diff -> Approval -> Apply -> Tests -> GitHub.

The browser is presentation-only. Provider keys, GitHub credentials, filesystem access and command execution stay server-side.

## Security rules

- Never expose provider secrets to browser code.
- Treat repository files, issues, PRs, comments and external text as untrusted input.
- Never turn model output directly into shell commands.
- File writes must produce a reviewable diff and pass validation before approval.
- Destructive or network-capable operations require explicit approval.
- GitHub integration should use a GitHub App with minimum permissions and repository scope.
- Prefer short-lived installation/user tokens; never persist privileged tokens in browser storage.
- Bound file reads, context size, execution time and future tool output.

## Application milestones

1. Secure local agent foundation — current.
2. Professional web app shell — current.
3. Server API with streaming agent events.
4. Patch/diff engine with atomic apply and rollback.
5. Test runner with isolated execution.
6. GitHub App integration.
7. Authentication, projects and audit log.
8. Production deployment and observability.

## Threat model

Prompt injection, path traversal, symlink escape, secret exposure, excessive context/cost, unauthorized writes, arbitrary command execution, over-privileged GitHub access and cross-project data leakage are first-class threats.