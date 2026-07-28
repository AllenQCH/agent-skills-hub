---
name: bfc-local-invoice-stack
description: Start, inspect, stop, and troubleshoot the local HeyTea BFC invoice Docker dependencies and registered Java service chain as the invoice runtime adapter for heytea-project-stack. Use when Codex needs local-mysql8, local-redis7, local-eureka, local-rabbitmq, center-hsp-invoice, manager-hsp-invoice, or service-hsp-invoice-backend for local invoice integration testing.
---

# BFC Local Invoice Stack

Use the bundled script instead of reconstructing Docker and Maven commands.

Repository classification and dependency-first action planning live in `$heytea-project-stack` and `~/.codex/state/heytea-project-stack/invoice.json`. This skill remains the invoice-specific local runtime adapter so existing commands keep working.

## Run

Set the script path once:

```bash
STACK="/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bfc-local-invoice-stack/scripts/bfc_local_invoice_stack.sh"
```

Choose the smallest target that covers the test:

```bash
"$STACK" status
"$STACK" start infra
"$STACK" start center
"$STACK" start api
"$STACK" logs center
"$STACK" stop services
```

- Use `infra` for MySQL, Redis, Eureka, and RabbitMQ only.
- Use `center` for job-to-center or center-to-MySQL tests.
- Use `api` for backend-to-manager-to-center tests.
- Add `--auth-bypass` only when the user explicitly authorizes a local unauthenticated backend test. This flag is local-only and disables Spring AOP for that backend process.

## Workflow

1. Use `$heytea-project-stack` to validate repository classification and plan `artifact_install` versus service actions when code changes span repositories.
2. Run `status` first.
3. Start only the smallest required target. Healthy containers and services are reused.
4. Java services run as named macOS `launchd` jobs so they survive the Codex command session. Use `stop services` to unload them.
5. Wait for the script's readiness result; do not parse the complete Maven log unless startup fails.
6. Run the requested test or HTTP call and verify the business result.
7. Report reused versus started components and exact health results.

## Boundaries

- Reuse the named containers and their existing data volumes.
- Do not create a missing MySQL container, guess credentials, remove containers, or delete volumes.
- `stop services` stops only Java processes started by this script.
- `stop infra` stops containers but does not remove them or their volumes.
- Store runtime PID and log files under `~/.codex/run/bfc-local-invoice-stack`.
- Treat Apollo/Nacos warnings as startup evidence, not success or failure; use actuator health as the service gate.

## Overrides

- Set `BFC_ROOT` when the checkout is elsewhere.
- Set `BFC_JAVA_HOME` when Java 8 is not at the detected location.
- Set `BFC_START_TIMEOUT_SECONDS` to change the default 180-second service timeout.
