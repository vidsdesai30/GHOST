# GHOST Security Checklist

Evidence below refers only to files and checks in this local research prototype. Synthetic lab data only.

| Area | Status | Verification evidence | Remaining gap |
|---|---|---|---|
| Authentication/account security and passwords | NOT IMPLEMENTED | No auth dependency, password handling, login route, or account lifecycle exists. | Add an identity provider; never implement ad hoc password storage. |
| Sessions | NOT IMPLEMENTED | No session or cookie handling exists. | Add short-lived, rotated server-side sessions if a web deployment is introduced. |
| MFA | NOT IMPLEMENTED | No identity flow exists. | Enforce MFA through the identity provider. |
| Authorization/RBAC | NOT IMPLEMENTED | No authorization middleware or roles exist. | Add least-privilege roles and route tests. |
| Tenant isolation | NOT IMPLEMENTED | Single local SQLite database; no tenant key. | Add tenant-scoped storage and authorization tests. |
| Input validation | IMPLEMENTED | Pydantic field constraints and control-character rejection in `backend/models.py`; event batches capped at 500; request size middleware caps bodies at 1 MB in `backend/app.py`; invalid-input test passes. | Expand field-specific limits and fuzz testing. |
| Error security | PARTIAL | API uses typed validation and avoids returning stack traces. | Add consistent exception handlers and security event logging. |
| Backend/API security | PARTIAL | CORS allows only configured local origins, methods/headers are restricted, request bodies are bounded, and no dynamic shell execution exists. | Add auth, rate limiting, TLS at deployment, CSRF strategy, and dependency scanning. |
| Logging/monitoring | PARTIAL | Python logger is configured with environment-controlled level. | Add structured audit events, redaction, retention, and alerting. |
| Data protection | PARTIAL | Synthetic-only policy, `.env`/SQLite ignored, no secrets in examples. | Add encryption, access controls, retention and deletion policy. |
| Dependencies | PARTIAL | Versions are pinned in `backend/requirements.txt`; frontend dependencies are declared. | Generate lockfiles and run vulnerability scanning. |
| Deployment | NOT IMPLEMENTED | README only documents local uvicorn/Vite commands. | Add hardened container/deployment configuration and secret management. |
| Tests | IMPLEMENTED | `backend/test_app.py` and `backend/test_detection.py` pass 10 tests; frontend `npm run build` passes; live browser validation covered all dashboard views. | Add automated property, integration, security, and browser tests. |

This checklist deliberately does not claim prototype limitations are controls.
