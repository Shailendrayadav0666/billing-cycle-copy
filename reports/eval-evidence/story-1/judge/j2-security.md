# J2 — Security (OWASP Top 10:2025) — Story 1

**Rubric**: `tests/.evals/rubrics/security-rubric.json` v1.0.0
**Judge model**: claude-sonnet-5

| ID | OWASP | Criterion | Weight | Score | Citation |
|---|---|---|---|---|---|
| SEC-01 | A01:2025 | Broken access control | 0.25 | 1.0 | Both new endpoints check `email not in users` before touching `billing_data`, identical to the existing `GET /api/billing` convention — no new gap introduced |
| SEC-02 | A06:2025 | Insecure design | 0.20 | 1.0 | `prorated_charge` is recomputed server-side inside `upgrade()` from stored `renew_at`, never trusted from a client value; already-Premium guard present on both endpoints |
| SEC-03 | A07:2025 | Authentication failures | 0.20 | 1.0 | No new endpoint bypasses the existing email-as-token check; no new weakening introduced by this diff |
| SEC-04 | A08:2025 | Software/data integrity | N/A | N/A | This story's diff does not touch `.github/workflows/agentic-eval-pipeline.yml` — criterion not exercised, excluded, weight renormalised |
| SEC-05 | A10:2025 | Mishandling exceptional conditions | 0.10 | 1.0 | `402`/`409` responses disclose only the documented `detail`/`message` fields; no mutation occurs on the declined-payment or already-premium branches |
| SEC-06 | A03:2025 | Software supply chain | 0.10 | 1.0 | Zero new pip/npm dependencies added (confirmed against `requirements.txt` and `package.json` diffs) |

Renormalised weights (SEC-04 excluded): SEC-01 0.294, SEC-02 0.235, SEC-03 0.235, SEC-05 0.118, SEC-06 0.118 — sum 1.0.

**J2 = 1.00** — **PASS** (≥ `llmJudgeSecurityScoreMin` 0.85 from `tests/.evals/config.json`)

## Advisory (pre-existing, out of scope — not scored, not a finding)
- Wildcard CORS (`allow_origins=["*"]`, `main.py:14`) — pre-existing, not introduced or touched by this story.
- Email-as-bearer-token authentication — pre-existing POC design choice, not introduced or touched by this story.
