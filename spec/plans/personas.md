# Personas — Self-Serve Premium Upgrade

## Persona 1: Standard Plan Subscriber

- **Role**: An existing Billing-Cycle user currently on the Standard plan ($20/month).
- **Goals**: Wants more chat credits, chatbots, and document-page capacity without waiting for the
  next billing cycle or contacting support.
- **Pain point** (from the Epic/PRD): the Billing page tells them on-demand credit is unavailable on
  their plan, but offers no path to change that — friction that risks churn.
- **Technical context**: Interacts only through the existing React frontend (`Billing.jsx`); has no
  visibility into the backend's in-memory data model or auth mechanism.
- **Success**: Completes the upgrade in under 60 seconds, sees the correct prorated charge before
  committing, and immediately sees updated plan/usage limits with no disruption to the rest of the
  Billing page.

This is the single persona this Epic serves — the Epic and PRD name no other user type (no admin
persona, no support-agent persona) and the Out of Scope section explicitly excludes admin
reporting.
