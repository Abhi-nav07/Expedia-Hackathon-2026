# Patch for frontend/package.json (from Module 1)

## Security fix — required

Module 1 pinned `next@14.2.15`. Since then, Next.js disclosed several
CVEs against the App Router (RSC-protocol denial-of-service and, in one
case, a remote-code-execution track — see
https://nextjs.org/blog/security-update-2025-12-11 and
https://nextjs.org/blog/CVE-2025-66478). All are fixed in `14.2.35`,
the final patch release for the 14.x line.

Change:
```json
"next": "14.2.15",
```
to:
```json
"next": "14.2.35",
```
and correspondingly:
```json
"eslint-config-next": "14.2.15",
```
to:
```json
"eslint-config-next": "14.2.35",
```

Then reinstall:
```bash
cd frontend && npm install
```

## Longer-term consideration (not required right now)

Next.js 14 reached end-of-life in October 2025 — `14.2.35` is the last
security patch that line will ever receive. For a hackathon-timeline
project this is an acceptable, pragmatic fix. If there's time before
submission (or for anyone extending this repo afterward), moving to a
maintained major (Next 15.x) is worth it for guaranteed future CVE
coverage. That's a larger, breaking change (App Router behavior shifts,
some config option renames) and out of scope for this module — flagging
it here rather than making that call silently.
