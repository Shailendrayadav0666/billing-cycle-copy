# Personas — Mid-Cycle Subscription Upgrade

## Persona 1: Standard Subscriber ("Priya")
- **Role**: Existing user on the Standard plan ($20/mo)
- **Characteristics**: Active user of the Tasks/Billing app; identified in the backend by email (email-as-token auth pattern); sees her current plan, usage, and renewal date on the Billing page.
- **Motivation**: Wants more chat credits / chatbots / document-page quota than Standard allows, and wants to upgrade without leaving the app or contacting support.
- **Pain point today**: No upgrade path exists — the Billing page shows a static "Standard" badge with no call to action.
- **Relevant to**: Story 1 (all ACs — CTA visibility, proration preview, upgrade execution both happy and declined paths).

## Persona 2: Premium Subscriber ("Priya, post-upgrade" / "Deepak, existing Premium user")
- **Role**: A user already on the Premium plan ($40/mo) — either freshly upgraded via this feature, or an existing Premium user in the mock data.
- **Characteristics**: Sees Premium quotas (10,000 chat credits / 10 chatbots / 5,000 document pages) and the Premium price on the Billing page.
- **Motivation**: Should not be confused by an upgrade CTA that no longer applies to them.
- **Pain point avoided**: Being offered a redundant "Upgrade to Premium" action, or being able to trigger a second, meaningless upgrade call.
- **Relevant to**: Story 1 (Already-Premium guard AC).

## Persona Mapping

| Persona | Story |
|---|---|
| Standard Subscriber | Story 1 |
| Premium Subscriber | Story 1 |
