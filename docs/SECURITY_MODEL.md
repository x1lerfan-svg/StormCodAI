# StormCodAI Security Model

StormCodAI treats repository content, issue text, pull requests, comments, generated code, and external model output as untrusted data.

## Core boundaries

- Provider credentials stay server-side.
- The browser never receives provider API keys.
- Workspace paths must remain inside the configured workspace.
- Symlink access is rejected.
- Secret-like files are excluded from model context.
- Secret-like values in text are redacted before context assembly.
- Model output is advisory until a future approval/diff pipeline applies it.
- GitHub credentials will be introduced through least-privilege, short-lived credentials rather than browser storage.
- Destructive or network-capable tools require explicit policy checks and approval.

## Agent safety

The model cannot grant itself new tools. Tool availability is controlled by application code. Repository text is explicitly framed as untrusted evidence so prompt injection in a repository cannot become an application instruction.

## Verification target

The web/API layer is developed against OWASP ASVS concepts, especially validation, access control, error handling, data protection, communication, malicious-code resistance, file/resource handling, API security, and secure configuration.

GitHub Actions follow least-privilege permissions and immutable action references where third-party actions are used.

## Future high-risk components

Before enabling command execution, GitHub write access, or automatic patch application, StormCodAI must add:

1. explicit capability/permission policy;
2. isolated execution;
3. resource/time limits;
4. reviewable unified diffs;
5. atomic apply and rollback;
6. audit events without secrets;
7. test and security gates;
8. user approval for high-impact actions.
