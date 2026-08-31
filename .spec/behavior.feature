# Cycle-level behaviour spec — EPIC-1 Mid-Cycle Subscription Upgrade
#
# Written ONCE per cycle at the STOP CHECKPOINT, per common/behavior-spec.md Section 3.
# Holds only the journeys that SPAN work units — those no single story owns.
# This is what the B3 tier runs on the last work unit of the cycle.
#
# ============================================================================
# RECORDED EXPLICITLY: THIS CYCLE HAS NO GENUINE CROSS-UNIT JOURNEYS.
# ============================================================================
#
# Reason: target_story_count was set to 1 by explicit user override (audit.md
# Entries 10-11). The cycle contains exactly one work unit, Story 1.1, which
# owns the entire Standard-to-Premium upgrade journey end to end — the CTA, the
# proration quote, the payment, the state mutation and both outcome paths.
#
# A "cross-unit" journey requires at least two units for a journey to span.
# With one unit, every scenario worth writing is already a Story 1.1 scenario
# and lives in:
#
#     .spec/aire-docs/implementation/code/behavior/story-1.1.feature
#
# Copying those scenarios here would violate the Section 3 rule directly:
# "Not a copy of the per-story scenarios. If it only restates what individual
#  stories already cover, it is adding nothing — write the genuine cross-unit
#  journeys, or record explicitly that the requirement has none."
#
# This file is that explicit record. It is deliberately scenario-free.
#
# ----------------------------------------------------------------------------
# B3 tier behaviour for this cycle
# ----------------------------------------------------------------------------
# B3 runs on the last work unit and executes this file plus every other feature
# file. With no scenarios here, B3 reduces to B2 (the accumulated suite) for
# this cycle. That is the correct outcome, not a gap: B1 and B2 still run in
# full against story-1.1.feature, so the upgrade journey is fully gated.
#
# ----------------------------------------------------------------------------
# What WOULD belong here, had the story set been sliced as recommended
# ----------------------------------------------------------------------------
# Recorded so a future cycle on this Epic does not have to re-derive it. Under
# the recommended 10-story split, these journeys would have spanned units and
# earned a place in this file:
#
#   - Register a brand-new account (registration flow, pre-existing) and then
#     upgrade it, proving the registration-seeded billing record is upgradable
#     and not only the seed user's.
#   - Upgrade, then reload the page from cold, proving the Premium state is
#     served by GET /api/billing rather than held only in React state.
#   - Attempt an upgrade with a declined card, then retry successfully in the
#     same session, proving the failed attempt left no residue.
#
# All three are currently covered inside story-1.1.feature because one unit owns
# the whole journey. They are listed here as the seam a future split would use.
#
# ----------------------------------------------------------------------------
# Requirement traceability
# ----------------------------------------------------------------------------
# Every requirement ID (FR-1..FR-13, NFR-1..NFR-7, SEC-1..SEC-6) is traced to a
# Story 1.1 acceptance criterion in the coverage matrix at the end of
# .spec/aire-docs/planning/user-stories/stories.md — 26/26 fully covered. No
# requirement depends on a cross-unit journey for its coverage, which is the
# substantive reason this file is empty rather than an oversight.
