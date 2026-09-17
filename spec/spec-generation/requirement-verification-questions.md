# Requirements Clarification Questions — Self-Serve Premium Upgrade

The Epic and its parent PRD (both pulled from Atlas) are detailed and already answer most functional
questions (button placement, confirmation flow, proration formula, usage-limit table, 10 acceptance
criteria). The items below are the genuine open questions the PRD itself flags (OQ-2, OQ-3), plus gaps
the Atlas Deep Dive surfaced that this Epic's scope doesn't explicitly address, plus the two mandatory
extension opt-ins.

## Question 1 — Proration preview mechanism (PRD OQ-2 / Epic OQ-1)

Should the prorated-charge preview (shown in the confirmation panel before the user commits) use a
separate read-only endpoint, or a `dry_run` query parameter on the same `POST /api/billing/upgrade` endpoint?

A) Single endpoint with `?dry_run=true` — `POST /api/billing/upgrade?dry_run=true` returns the prorated charge without committing; the same endpoint without the flag commits (PRD's own suggested default)

B) Separate read-only endpoint — e.g. `GET /api/billing/upgrade/preview` — keeps preview (safe, idempotent GET) and commit (POST) semantically distinct

C) Other (please describe after [Answer]: tag below)

[Answer]:a

## Question 2 — On-demand balance on upgrade (PRD OQ-3 / Epic OQ-2)

`billing_data[email].usages` totals carry over on upgrade per FR-06 (used amounts are not reset). But
the separate `on_demand_usage` balance (currently unavailable/zero for Standard users) isn't addressed
by FR-06. What should happen to it on upgrade?

A) Carry over as-is (starts at whatever it currently is — effectively 0, since Standard users can't accrue on-demand usage) and becomes usable going forward

B) Reset to a Premium default/allowance on upgrade (a starting on-demand credit grant)

C) Other (please describe after [Answer]: tag below)

[Answer]:a

## Question 3 — Auth/security posture for the new endpoint

The Atlas Deep Dive flags the existing auth pattern (raw email as bearer token, plaintext password
storage) as 🔴 Critical security debt across the whole system. The PRD's own NFR section says the new
`/api/billing/upgrade` endpoint should use "the same auth pattern as other endpoints" (i.e. email
lookup only, no signature/expiry check) — consistent with the existing 6 endpoints, but it inherits the
same critical weakness (SECURITY-08, SECURITY-12 in the mandatory Security Baseline).

Should this Epic:

A) Match the existing pattern exactly (email-as-token, no auth rework) — accept the existing security
   debt as out of scope for this Epic; a system-wide auth overhaul (JWT + bcrypt) is a separate,
   future initiative, not blocking this feature

B) Harden authentication as part of this Epic — replace email-as-token with a signed token (JWT) and
   hash passwords (bcrypt), across all 6 existing endpoints plus the new one, before shipping the
   upgrade feature

C) Other (please describe after [Answer]: tag below)

[Answer]:a

## Question 4 — Concurrent upgrade requests

The Deep Dive notes in-memory dict read-modify-write sequences are not atomic under concurrent load
(observed for task-ID generation; the same class of risk applies to a user double-clicking "Confirm
Upgrade" or firing two near-simultaneous requests). PRD NFR already requires idempotency (second call
returns 400 "Already on Premium"), which covers sequential double-submits. Is basic idempotency
(check-then-set, matching the existing code style) sufficient, or is stronger concurrency protection
needed for this Epic?

A) Basic idempotency is sufficient (matches PRD NFR and the existing code's style/rigor) — no explicit
   locking needed for this POC-scale feature

B) Add explicit protection against a race between two near-simultaneous upgrade requests from the same
   user (e.g. a per-user lock or atomic check-and-set)

C) Other (please describe after [Answer]: tag below)

[Answer]:a

## Question 5 — Resiliency Baseline Extension (opt-in)

Should the resiliency baseline be applied to this project?

**What this extension is.** Enabling it applies a set of **directional, design-time best practices** for building resilient systems, derived from the **AWS Well-Architected Framework (Reliability Pillar)** and resilience-review guidance. It steers requirements, design, and code toward fault tolerance, high availability, observability, and recoverability — covering 15 practice areas across business goals, change management, observability, high availability, disaster recovery, and continuous improvement.

**What this extension is NOT.** Enabling it does **not** make your workload production-ready, nor does it certify or guarantee any availability, RTO, or RPO target. It is a **starting point** that scaffolds good resiliency decisions early — it is not a substitute for a formal **AWS Well-Architected Review** of the built system.

Treat the output as a well-grounded **first draft of your resiliency posture** to build on and validate — not a finished, production-certified result.

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance (recommended for business-critical workloads, as an informed starting point that you can validate and harden before go-live)

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

X) Other (please describe after [Answer]: tag below)

[Answer]:b

## Question 6 — Property-Based Testing Extension (opt-in)

Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)

X) Other (please describe after [Answer]: tag below)

[Answer]:c
