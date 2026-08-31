from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Billing & Tasks POC")

# Plan catalogue. Two rungs only - a third tier would need a general plan-ladder model.
#
# Annotated because the entries mix a float price with a str label; without it the value type is
# inferred as `object` and the proration arithmetic below is rejected.
PLANS: dict[str, dict[str, Any]] = {
    "Standard": {"price": 20.0, "label": "$20/month"},
    "Premium": {"price": 40.0, "label": "$40/month"},
}

# Premium quota ceilings, keyed by usage id.
#
# Deliberately an id -> total map rather than a list of complete usage objects: an upgrade raises
# the ceiling, it must not reset what the subscriber has already consumed. Assigning whole objects
# would overwrite "used" with 0.
PREMIUM_QUOTA_TOTALS = {
    "chat-credits": 10000,
    "chatbots": 10,
    "documents-pages": 5000,
}

DAYS_IN_CYCLE = 30

PREMIUM_ON_DEMAND_NOTICE = "On-demand credit is available on your Premium plan."

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory mock store (no database)
users: dict[str, dict[str, Any]] = {
    "tpg@example.com": {
        "id": 1,
        "name": "TPG",
        "email": "tpg@example.com",
        "password": "password",
        "plan": "Standard",
        "price": "$20/month",
        "renew_at": (datetime.today() + timedelta(days=30)).strftime("%b %d, %Y"),
    }
}

billing_data: dict[str, dict[str, Any]] = {
    "tpg@example.com": {
        "plan_name": "Standard",
        "price": "$20/month",
        "renew_at": (datetime.today() + timedelta(days=30)).strftime("%b %d, %Y"),
        "usages": [
            {
                "id": "chat-credits",
                "label": "Chat credits",
                "used": 100,
                "total": 2000,
                "help": "Messages used this billing cycle.",
            },
            {
                "id": "chatbots",
                "label": "Chatbots",
                "used": 1,
                "total": 3,
                "help": "Active chatbot agents out of the included limit.",
            },
            {
                "id": "documents-pages",
                "label": "Documents pages",
                "used": 15,
                "total": 1000,
                "help": "You can add 985 more pages of your documents.",
            },
        ],
        "included_usage": {
            "title": "Your included usage",
            "items": [
                {"id": "daily", "label": "Daily quota", "used_percent": 5, "resets_in": "23 hours"},
                {"id": "weekly", "label": "Weekly quota", "used_percent": 10, "resets_in": "5 days"},
            ],
            "help": "Usage included in your plan.",
        },
        "on_demand_usage": {
            "title": "On-demand usage",
            "remaining_balance": "$18.00",
            "your_usage": "$0.00",
            "help": "Additional usage charges beyond your included quota.",
            "notice": "On-demand credit is not available in standard plan for usage beyond your included quota.",
        },
    }
}

tasks_data: dict[str, list[dict[str, Any]]] = {
    "tpg@example.com": [
        {"id": 1, "title": "Review monthly invoice", "status": "pending", "due": "Today"},
        {"id": 2, "title": "Add team member", "status": "completed", "due": "Yesterday"},
        {"id": 3, "title": "Update billing address", "status": "pending", "due": "In 2 days"},
    ]
}


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class TokenRequest(BaseModel):
    token: str


class TaskCreateRequest(BaseModel):
    email: str
    title: str


class UpgradeRequest(BaseModel):
    email: str
    # Exactly one field, deliberately. There is no amount, plan or card field, so a caller cannot
    # supply their own price - not because it is validated away, but because there is nowhere to
    # put it. Pydantic drops unknown keys, so an "amount" in the body never reaches the handler.


def charge_card(email: str, amount: float) -> dict:
    """Dummy in-repo payment gateway. Deterministic on the email prefix.

    Pure: no network, no SDK, no clock, no randomness, no logging. The same email always yields
    the same result, which is what lets both paths be demonstrated on demand.

    `amount` is accepted and unused by this dummy so the signature matches a real gateway and
    callers already pass the right value.
    """
    if email.startswith("fail"):
        return {"status": "card_declined", "message": "Your card was declined."}
    return {"status": "success"}


def _resolve_upgrade_context(email: str) -> tuple[dict, int, float]:
    """The single implementation of the upgrade guard chain and the proration formula.

    Both upgrade endpoints call this. Keeping it in one place is what stops the preview from
    quoting a price the upgrade then refuses to honour.

    The guard ORDER is load-bearing: authenticating first means an unauthenticated caller cannot
    learn whether an email exists, has a billing record, or is already Premium.

    Returns (billing_record, days_remaining, prorated_charge).
    Raises 401 unauthenticated / 404 no billing record / 409 already premium.
    """
    if email not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    record = billing_data.get(email)
    if record is None:
        # Deliberately NOT falling back to another user's record the way GET /api/billing does.
        # A missing record is an error, never a substitution.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="billing_record_not_found"
        )

    if record["plan_name"] != "Standard":
        # Strict equality, so an unrecognised plan is refused rather than silently upgraded.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="already_premium")

    renew_at_date = datetime.strptime(record["renew_at"], "%b %d, %Y")
    days_remaining = max(1, (renew_at_date - datetime.today()).days)
    daily_delta = (PLANS["Premium"]["price"] - PLANS["Standard"]["price"]) / DAYS_IN_CYCLE
    prorated_charge = round(daily_delta * days_remaining, 2)

    return record, days_remaining, prorated_charge


def _premium_usages(existing: list[dict]) -> list[dict]:
    """Raise each quota ceiling to its Premium value, returning a NEW list.

    Pure: never mutates `existing`. Each entry is rebuilt by spreading the original, so id, label
    and used survive by default rather than by remembering to copy them.

    An entry whose id is not a known Premium quota is passed through untouched, so a future metric
    is not silently dropped by an upgrade.
    """
    upgraded: list[dict] = []
    for entry in existing:
        new_total = PREMIUM_QUOTA_TOTALS.get(entry["id"])
        if new_total is None:
            upgraded.append(entry)
            continue

        new_entry = {**entry, "total": new_total}
        if entry["id"] == "documents-pages":
            # Follows the convention the existing seed and registration data already use:
            # the help text states remaining capacity, i.e. total - used.
            remaining = new_total - entry["used"]
            new_entry["help"] = f"You can add {remaining} more pages of your documents."
        upgraded.append(new_entry)

    return upgraded


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    user = users.get(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": payload.email, "user": {k: v for k, v in user.items() if k != "password"}}


@app.post("/api/auth/register")
def register(payload: RegisterRequest):
    if payload.email in users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists")
    users[payload.email] = {
        "id": len(users) + 1,
        "name": payload.name,
        "email": payload.email,
        "password": payload.password,
        "plan": "Standard",
        "price": "$20/month",
        "renew_at": (datetime.today() + timedelta(days=30)).strftime("%b %d, %Y"),
    }
    billing_data[payload.email] = {
        "plan_name": "Standard",
        "price": "$20/month",
        "renew_at": (datetime.today() + timedelta(days=30)).strftime("%b %d, %Y"),
        "usages": [
            {
                "id": "chat-credits",
                "label": "Chat credits",
                "used": 0,
                "total": 2000,
                "help": "Messages used this billing cycle.",
            },
            {
                "id": "chatbots",
                "label": "Chatbots",
                "used": 0,
                "total": 3,
                "help": "Active chatbot agents out of the included limit.",
            },
            {
                "id": "documents-pages",
                "label": "Documents pages",
                "used": 0,
                "total": 1000,
                "help": "You can add 1000 more pages of your documents.",
            },
        ],
        "included_usage": {
            "title": "Your included usage",
            "items": [
                {"id": "daily", "label": "Daily quota", "used_percent": 5, "resets_in": "23 hours"},
                {"id": "weekly", "label": "Weekly quota", "used_percent": 10, "resets_in": "5 days"},
            ],
            "help": "Usage included in your plan.",
        },
        "on_demand_usage": {
            "title": "On-demand usage",
            "remaining_balance": "$0.00",
            "your_usage": "$0.00",
            "help": "Additional usage charges beyond your included quota.",
            "notice": "On-demand credit is not available in standard plan for usage beyond your included quota.",
        },
    }
    tasks_data[payload.email] = [
        {"id": 1, "title": "Explore the dashboard", "status": "completed", "due": "Today"},
    ]
    return {"access_token": payload.email, "user": {k: v for k, v in users[payload.email].items() if k != "password"}}


@app.get("/api/users/me")
def me(email: str):
    user = users.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {k: v for k, v in user.items() if k != "password"}


@app.get("/api/billing")
def billing(email: str):
    if email not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return billing_data.get(email, billing_data["tpg@example.com"])


@app.get("/api/billing/upgrade-preview")
def billing_upgrade_preview(email: str):
    """Prorated quote for a Standard -> Premium upgrade. Read-only: writes nothing, charges nothing.

    Safe to call repeatedly, which the UI does - once per click of the upgrade button.
    """
    record, days_remaining, prorated_charge = _resolve_upgrade_context(email)
    return {
        "current_plan": "Standard",
        "new_plan": "Premium",
        "days_remaining": days_remaining,
        "prorated_charge": prorated_charge,
        "next_renewal_price": PLANS["Premium"]["price"],
        "renew_at": record["renew_at"],
    }


@app.post("/api/billing/upgrade")
def billing_upgrade(payload: UpgradeRequest):
    """Charge the prorated amount and, only on success, flip the plan to Premium.

    Three zones, and the boundaries between them are what make the mutation all-or-nothing without
    a transaction:

      Zone A - read, validate, compute, charge. May raise freely; writes nothing. The declined
               branch returns from here, so Zone C is unreachable on that path.
      Zone B - build the new values. Pure; still writes nothing.
      Zone C - the only writes in this function. Plain dict assignments on already-resolved values,
               with no call, arithmetic, parse or await between them, so none of them can raise.

    renew_at is preserved by omission: no line below assigns it, in either store.
    """
    # ---- Zone A: read, validate, compute, charge. Nothing is written here. ----
    record, _days_remaining, prorated_charge = _resolve_upgrade_context(payload.email)

    # The amount is recomputed from stored state on every call and never read from the request,
    # so the client cannot influence what it is charged.
    result = charge_card(payload.email, prorated_charge)
    if result["status"] != "success":
        # HTTPException serialises to a single "detail" key, which cannot express the two-key body
        # this contract requires, so the response is built explicitly.
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"detail": "card_declined", "message": result["message"]},
        )

    # ---- Zone B: build. Pure; still nothing written. ----
    #
    # Every container that Zone C writes into is resolved HERE, not there. A nested subscript such
    # as record["on_demand_usage"]["notice"] can raise KeyError, and as the last of six writes it
    # would leave the record billed as Premium while its quotas and notice still said Standard.
    # Resolving the containers up front moves that failure ahead of the first write, so the
    # mutation stays all-or-nothing.
    new_usages = _premium_usages(record["usages"])
    premium_label = PLANS["Premium"]["label"]
    user_record = users[payload.email]
    on_demand = record["on_demand_usage"]

    # ---- Zone C: the only writes. Plain assignments on resolved objects; none of these can raise.
    user_record["plan"] = "Premium"
    user_record["price"] = premium_label
    record["plan_name"] = "Premium"
    record["price"] = premium_label
    record["usages"] = new_usages
    on_demand["notice"] = PREMIUM_ON_DEMAND_NOTICE

    return {"status": "success", "plan": "Premium", "charge": prorated_charge}


@app.get("/api/tasks")
def tasks(email: str):
    if email not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return tasks_data.get(email, [])


@app.post("/api/tasks")
def add_task(payload: TaskCreateRequest):
    if payload.email not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_tasks = tasks_data.setdefault(payload.email, [])
    new_id = max((t["id"] for t in user_tasks), default=0) + 1
    new_task = {"id": new_id, "title": payload.title, "status": "pending", "due": "Today"}
    user_tasks.append(new_task)
    return new_task


# Serve the built frontend if it exists (production build)
dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_dir.is_dir():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
