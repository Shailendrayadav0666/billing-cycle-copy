from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timedelta

app = FastAPI(title="Billing & Tasks POC")

# Plan pricing + Premium quotas for the Mid-Cycle Subscription Upgrade epic.
PLANS: dict = {
    "Standard": {"price": 20.0, "label": "$20/month"},
    "Premium": {"price": 40.0, "label": "$40/month"},
}
PREMIUM_QUOTAS: dict = {
    "usages": [
        {
            "id": "chat-credits",
            "label": "Chat credits",
            "total": 10000,
            "help": "Messages used this billing cycle.",
        },
        {
            "id": "chatbots",
            "label": "Chatbots",
            "total": 10,
            "help": "Active chatbot agents out of the included limit.",
        },
        {
            "id": "documents-pages",
            "label": "Documents pages",
            "total": 5000,
            "help": "You can add 5000 more pages of your documents.",
        },
    ]
}
DAYS_IN_CYCLE = 30

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory mock store (no database)
users: dict = {
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

billing_data: dict = {
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

tasks_data = {
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


def charge_card(email: str, amount: float) -> dict:
    """Deterministic dummy payment gateway (no external SDK/network call)."""
    if email.startswith("fail"):
        return {"status": "card_declined", "message": "Your card was declined."}
    return {"status": "success"}


def _compute_proration(email: str) -> dict:
    """Server-side-only proration math (ARCH-01). Raises HTTPException on already-Premium."""
    if billing_data[email]["plan_name"] == "Premium":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="already_premium")
    renew_at: str = billing_data[email]["renew_at"]
    renew_at_date: datetime = datetime.strptime(renew_at, "%b %d, %Y")
    days_remaining: int = max(1, (renew_at_date - datetime.today()).days)
    daily_delta = (PLANS["Premium"]["price"] - PLANS["Standard"]["price"]) / DAYS_IN_CYCLE
    prorated_charge = round(daily_delta * days_remaining, 2)
    return {
        "current_plan": "Standard",
        "new_plan": "Premium",
        "days_remaining": days_remaining,
        "prorated_charge": prorated_charge,
        "next_renewal_price": PLANS["Premium"]["price"],
        "renew_at": renew_at,
    }


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


@app.get("/api/billing/upgrade-preview")
def upgrade_preview(email: str):
    if email not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return _compute_proration(email)


@app.post("/api/billing/upgrade")
def upgrade(payload: UpgradeRequest):
    email = payload.email
    if email not in users:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    preview = _compute_proration(email)  # raises 409 already_premium before any side effect
    result = charge_card(email, preview["prorated_charge"])

    if result["status"] == "card_declined":
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"detail": "card_declined", "message": result["message"]},
        )

    users[email]["plan"] = "Premium"
    users[email]["price"] = PLANS["Premium"]["label"]
    billing_data[email]["plan_name"] = "Premium"
    billing_data[email]["price"] = PLANS["Premium"]["label"]

    existing_usage_by_id = {u["id"]: u["used"] for u in billing_data[email]["usages"]}
    billing_data[email]["usages"] = [
        {**quota, "used": existing_usage_by_id.get(quota["id"], 0)} for quota in PREMIUM_QUOTAS["usages"]
    ]
    billing_data[email]["on_demand_usage"]["notice"] = "On-demand credit is available on your Premium plan."

    return {"status": "success", "plan": "Premium", "charge": preview["prorated_charge"]}


# Serve the built frontend if it exists (production build)
dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_dir.is_dir():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
