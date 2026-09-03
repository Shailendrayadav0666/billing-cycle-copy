# Baseline Static Eval Evidence — Story 1

**Captured**: 2026-09-03T16:39:11Z, before any code generation, on story/1-mid-cycle-subscription-upgrade (cut from the epic branch).

| Check | Tool | Result | Notes |
|---|---|---|---|
| D1 Lint (backend) | ruff (bootstrapped `src/backend/ruff.toml`) | PASS — 0 findings | |
| D1 Lint (frontend) | oxlint (`npm run lint`) | 4 pre-existing warnings | Tasks.jsx:17, AuthContext.jsx:19 (x2), AuthContext.jsx:66 — none in files this story touches beyond Billing.jsx |
| D2 Types (backend) | mypy (bootstrapped `src/backend/mypy.ini`) | 2 pre-existing errors | main.py:203 (`max()` on a mixed-type default) — pre-existing, not this story's code |
| D3 SAST | semgrep --config auto (backend) | 1 pre-existing finding | `python.fastapi.security.wildcard-cors.wildcard-cors` at main.py:12 — pre-existing CORS wildcard, this story does not touch CORS config |
| D4 Deps | pip-audit (backend) | PASS — no known vulnerabilities | |
| D5 Licences | not run at baseline (no dependency changes planned) | N/A | |
| D6 Complexity | radon cc (backend main.py, venv excluded) | PASS — no function exceeds threshold C | |
| D7 Secrets | gitleaks (native binary — Podman machine failed to start on this Windows host, see note below) | PASS — no leaks found | |

## Podman note (environment-specific, does not affect CI)
Podman IS installed (`podman machine list` shows `podman-machine-default`), but `podman machine start` failed twice on this Windows host with `machine did not transition into running state: ssh error: machine not in running state` (a WSL2/Hyper-V VM transition issue local to this dev machine). This is NOT the "Podman not installed" exception in `common/behavior-spec.md` Section 5.1, but functionally equivalent for this session: no working container runtime is available here. D7 above used gitleaks' native Windows binary (the Section 2.4.1 install chain's "alternative installer" rung) rather than the Podman OCI-image rung. **The epic-level smoke test already proved Podman works correctly in the real CI environment** (GitHub Actions `ubuntu-latest`, run 33745286732) — this is a local-Windows-only limitation, not a gap in the merge-gating pipeline. The Behavioural Gherkin gate (Step 6.1) will record the same native-fallback exception for the same reason, with results marked `PASS (unverified parity)`.
