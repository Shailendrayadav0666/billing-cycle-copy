# Personas — EPIC-1 Mid-Cycle Subscription Upgrade

**Epic**: EPIC-1 — Mid-Cycle Subscription Upgrade (Standard → Premium)
**Source**: derived from `epic-brief.md` (Atlas doc 3157) and the existing auth/billing flows in `knowledge-graph.md` (Atlas doc 3155)
**Created**: 2026-08-31

---

## P1 — Standard Subscriber *(primary)*

| Attribute | Detail |
|---|---|
| **Who** | An authenticated user on the Standard plan ($20/month), e.g. the seed user `tpg@example.com` |
| **Goal** | Move to Premium without leaving the app, contacting support, or waiting for the next billing cycle |
| **Motivation** | Has hit or is approaching a Standard quota — 2,000 chat credits, 3 chatbots, or 1,000 document pages — and wants the Premium ceilings now |
| **Context** | Signed in; `token` is their email; lands on `/billing` after login |
| **Pain today** | The Billing page shows a hardcoded `Standard` badge and a static plan card. There is no upgrade path in the product at all. |
| **What success looks like** | Sees an upgrade CTA, is told the exact prorated amount **before** committing, confirms once, and immediately sees Premium reflected in the plan card and every quota |
| **Key concern** | Not being surprised by the charge. They must see the amount and the next renewal price before the money moves. |
| **Stories** | 1.1 |

---

## P2 — Premium Subscriber *(guard case)*

| Attribute | Detail |
|---|---|
| **Who** | An authenticated user already on Premium ($40/month) — including a Standard subscriber who just upgraded in this session |
| **Goal** | Manage and review their plan without being nudged toward an upgrade they already have |
| **Context** | `billing_data[email]["plan_name"] == "Premium"` |
| **Pain today** | Does not exist yet — no user can reach Premium in the product today. This persona is created *by* this Epic. |
| **What success looks like** | No upgrade CTA anywhere on the Billing page; if the endpoints are called directly they answer **409 `already_premium`** rather than charging again |
| **Key concern** | Never being double-charged, and never being confused into attempting a redundant upgrade |
| **Stories** | 1.1 |

---

## P3 — Demo Presenter *(deterministic-failure case)*

| Attribute | Detail |
|---|---|
| **Who** | Whoever demonstrates the flow — sales engineer, product owner, or the ve validating both branches |
| **Goal** | Show the card-declined path on demand, reliably, with no external payment provider and no UI toggle |
| **Mechanism** | Registers or logs in with an email starting with `fail` (e.g. `fail@example.com`). `charge_card()` then deterministically returns `card_declined`. |
| **Why this persona exists** | The Epic's gateway spec is built around this trigger prefix. It is a first-class requirement, not a test detail — the whole point of the dummy gateway is that both paths are demonstrable at will. |
| **What success looks like** | The declined path shows a clear inline error, the modal stays open, and **nothing in `users` or `billing_data` is mutated** — the presenter can retry or cancel and the account is untouched |
| **Key concern** | Determinism. The same email must always produce the same gateway outcome, with no network dependency. |
| **Stories** | 1.1 |

---

## Non-personas — explicitly out of scope

| Not a persona this cycle | Why |
|---|---|
| Downgrading subscriber (Premium → Standard) | Downgrades are out of scope per the Epic |
| Enterprise-tier prospect | No Enterprise tier exists; out of scope |
| Billing administrator managing another user's plan | No multi-user or admin model exists; `users` is keyed by the caller's own email |
| Refund requester | Refunds and credits are out of scope |
