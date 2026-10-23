# GHOST Security Checklist

This checklist describes the browser-only research demonstration. It is not a production security certification. Synthetic fixture data only.

| Area | Status | Evidence in this implementation | Remaining gap |
|---|---|---|---|
| Synthetic-data boundary | IMPLEMENTED | Fixtures are deterministic and use documentation-safe lab values. | Add governance and review before introducing any external data. |
| Network dependency | IMPLEMENTED | Detection and UI state run locally; no API or hosted inference requests exist. | A future service would need a reviewed trust boundary. |
| Input validation | LOCAL ONLY | TypeScript contracts and fixed fixture construction constrain the demo path. | Add server-side validation before accepting external telemetry. |
| Authentication and sessions | NOT IMPLEMENTED | No identity, cookie, or session system exists. | Use a reviewed identity provider for any deployment. |
| Authorization / RBAC | NOT IMPLEMENTED | Frontend navigation is not access control. | Enforce authorization on a backend, not in UI state. |
| MFA | NOT IMPLEMENTED | No identity flow exists. | Require MFA through the identity provider. |
| Tenant isolation | NOT IMPLEMENTED | No tenant concept or server storage exists. | Design tenant-scoped storage and authorization tests. |
| Persistence and retention | NOT IMPLEMENTED | Investigations exist only in React state. | Add access-controlled durable storage and retention rules. |
| Audit logging | NOT IMPLEMENTED | Security & Audit is an explanatory UI, not an audit stream. | Implement immutable, redacted server-side audit events. |
| Secrets and environment files | IMPLEMENTED | `.gitignore` excludes environment files, credential patterns, keys, and generated databases. | Review repository state before every publish. |
| Production deployment | NOT IMPLEMENTED | The documented run mode is a local Vite development/preview workflow. | Add TLS, headers, dependency scanning, monitoring, and incident response. |

## Ethical scope

GHOST must not be connected to sensitive production telemetry in its current form. A predicted action is a hypothesis, not an alert verdict or proof of activity. Do not add credential collection, attack execution, scanning, or live telemetry to the demonstration.
