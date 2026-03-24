import logging
import secrets
import uuid
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title="OFW Pro")

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

AUTH_USERNAME = "demo"
AUTH_PASSWORD = "demo"


@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    host = request.client.host if request.client else ""
    if host in ("127.0.0.1", "localhost", "::1"):
        return await call_next(request)
    if request.url.path.startswith("/static"):
        return await call_next(request)
    # Allow client view without auth
    if "/client" in request.url.path:
        return await call_next(request)
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Basic "):
        import base64
        try:
            decoded = base64.b64decode(auth[6:]).decode("utf-8")
            username, password = decoded.split(":", 1)
            if secrets.compare_digest(username, AUTH_USERNAME) and secrets.compare_digest(password, AUTH_PASSWORD):
                return await call_next(request)
        except Exception:
            pass
    return Response(
        content="Unauthorized", status_code=401,
        headers={"WWW-Authenticate": 'Basic realm="OFW Pro"'},
    )


# --- Demo Data ---

CURRENT_USER = {
    "first_name": "Brian",
    "last_name": "Olson",
    "initials": "BO",
    "email": "brian.olson@lawfirm.com",
    "role": "attorney",
    "avatar_color": "#0E8DA2",
}

FAMILIES = [
    {
        "id": "fam-1",
        "name": "Gein - Gein",
        "notification_settings": True,
        "members": [
            {"name": "Aaron Gein", "initials": "AG", "color": "#0E8DA2", "subscription": "Subscription: Current", "sub_detail": "Expires: 12/2026", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": False},
            {"name": "Jordan Gein", "initials": "JG", "color": "#4CAF50", "subscription": "Subscription: Current", "sub_detail": "Expires: 12/2026", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": False},
        ],
    },
    {
        "id": "fam-2",
        "name": "Markerson - Frederson",
        "notification_settings": False,
        "members": [
            {"name": "Boris Markerson", "initials": "BM", "color": "#7B1FA2", "subscription": "Subscription: Basic Volunteer", "sub_detail": "", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": False},
            {"name": "Fran Frederson", "initials": "FF", "color": "#E64A19", "subscription": "Subscription: Never subscribed", "sub_detail": "", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": True},
        ],
    },
    {
        "id": "fam-3",
        "name": "Markerson - Markerson",
        "notification_settings": False,
        "members": [
            {"name": "Stuart Markerson", "initials": "SM", "color": "#00796B", "subscription": "Subscription: Basic Volunteer", "sub_detail": "", "access": "Access Requested", "access_detail": "on 10/14/2024 by 3 family", "approved": False},
            {"name": "Fred Markerson", "initials": "FM", "color": "#C2185B", "subscription": "Subscription: Never subscribed", "sub_detail": "", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": True},
        ],
    },
    {
        "id": "fam-4",
        "name": "OFWTest-Wallner - OFWTest-Wallner",
        "notification_settings": True,
        "members": [
            {"name": "Annika OFWTest-Wallner", "initials": "AO", "color": "#0E8DA2", "subscription": "Subscription: Current", "sub_detail": "Expires: 12/2026", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": True},
            {"name": "Andrea OFWTest-Wallner", "initials": "AW", "color": "#388E3C", "subscription": "Subscription: Current", "sub_detail": "Expires: 12/2026", "access": "Access: Requested", "access_detail": "on 7/15/2025 by 3 family", "approved": True},
        ],
    },
]

MESSAGES = [
    {
        "id": "msg-1",
        "sender": "Annika OFWTest-Wal...",
        "sender_full": "Annika OFWTest-Wallner",
        "date": "Mar 3, 2025",
        "subject": "test available services",
        "preview": "This is a test message about available services...",
        "body": "Hi Brian,\n\nI wanted to reach out regarding the available services for our case. Could we schedule a time to discuss the parenting plan details?\n\nBest regards,\nAnnika",
        "unread": True,
        "folder": "inbox",
    },
]

INBOX_COUNT = 1
ACTION_ITEMS_COUNT = 2
NOTIFICATIONS_COUNT = 2

PARENTING_PLAN_SECTIONS = [
    "Child/ren",
    "Schedules",
    "Physical custody",
    "Legal custody",
    "Moving",
    "Exchanges",
    "Exchanges by flight",
    "Supervised visitation",
    "Changes to parenting time",
    "Access to child's information",
    "Health",
    "School",
    "Extracurricular activities",
    "Transportation",
    "Out-of-area travel",
    "Third-party contact",
    "Child care",
    "Child rearing",
    "Alcohol, tobacco and drugs",
    "Communication between parents",
    "Communication with child",
    "Expenses and money",
    "Taxes",
    "Child support",
    "Military",
    "Counseling",
    "Death",
    "Future revisions",
    "Signatures",
    "Miscellaneous",
]

# In-memory store for parenting plans
PARENTING_PLANS: dict = {}

# Demo schedule data
DEMO_SCHEDULES = [
    {
        "id": "sched-1",
        "name": "Standard Alternating Weeks",
        "parent_a": "Parent A",
        "parent_b": "Parent B",
        "pattern": "Week on / Week off",
        "start_date": "2026-04-01",
        "created": "2026-03-15",
    },
]


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/dashboard")


@app.get("/join/pro", response_class=HTMLResponse)
async def signup_page(request: Request):
    logger.info("Serving Pro signup page")
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/join/pro", response_class=HTMLResponse)
async def signup_submit(request: Request):
    logger.info("Processing Pro signup")
    return RedirectResponse(url="/onboarding", status_code=303)


@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request):
    logger.info("Serving onboarding page")
    return templates.TemplateResponse("onboarding.html", {"request": request})


@app.post("/onboarding", response_class=HTMLResponse)
async def onboarding_submit(request: Request):
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    logger.info("Serving Pro dashboard")
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "dashboard",
        "unread_messages": INBOX_COUNT,
        "families": FAMILIES,
    })


@app.get("/my-cases", response_class=HTMLResponse)
async def my_cases(request: Request):
    logger.info("Serving My Cases page")
    return templates.TemplateResponse("my_cases.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "my-cases",
        "families": FAMILIES,
    })


@app.get("/messages", response_class=HTMLResponse)
async def messages_page(request: Request):
    logger.info("Serving Messages page")
    return templates.TemplateResponse("messages.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "messages",
        "messages": MESSAGES,
        "inbox_count": INBOX_COUNT,
        "action_items_count": ACTION_ITEMS_COUNT,
        "notifications_count": NOTIFICATIONS_COUNT,
    })


@app.get("/custody-navigator", response_class=HTMLResponse)
async def custody_navigator(request: Request):
    logger.info("Serving Custody Navigator")
    return templates.TemplateResponse("custody_navigator.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "custody-navigator",
        "schedules": DEMO_SCHEDULES,
    })


@app.get("/parenting-plan/new", response_class=HTMLResponse)
async def parenting_plan_new(request: Request):
    logger.info("Serving Parenting Plan — Create")
    return templates.TemplateResponse("parenting_plan_new.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "parenting-plan",
    })


@app.post("/parenting-plan/new", response_class=HTMLResponse)
async def parenting_plan_create(request: Request):
    plan_id = str(uuid.uuid4())[:8]
    PARENTING_PLANS[plan_id] = {
        "id": plan_id,
        "created": datetime.now().isoformat(),
        "sections": {s: "" for s in PARENTING_PLAN_SECTIONS},
        "client_link": None,
        "status": "draft",
    }
    logger.info("Created parenting plan %s", plan_id)
    return RedirectResponse(url=f"/parenting-plan/{plan_id}", status_code=303)


@app.get("/parenting-plan/{plan_id}", response_class=HTMLResponse)
async def parenting_plan_edit(request: Request, plan_id: str):
    plan = PARENTING_PLANS.get(plan_id)
    if not plan:
        plan = {
            "id": plan_id,
            "created": datetime.now().isoformat(),
            "sections": {s: "" for s in PARENTING_PLAN_SECTIONS},
            "client_link": None,
            "status": "draft",
        }
        PARENTING_PLANS[plan_id] = plan
    return templates.TemplateResponse("parenting_plan_edit.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "parenting-plan",
        "plan": plan,
        "sections": PARENTING_PLAN_SECTIONS,
        "schedules": DEMO_SCHEDULES,
    })


@app.post("/parenting-plan/{plan_id}/send", response_class=HTMLResponse)
async def parenting_plan_send(request: Request, plan_id: str):
    plan = PARENTING_PLANS.get(plan_id)
    if plan:
        client_token = str(uuid.uuid4())[:8]
        plan["client_link"] = client_token
        plan["status"] = "sent"
    return RedirectResponse(url=f"/parenting-plan/{plan_id}", status_code=303)


@app.get("/parenting-plan/{plan_id}/client", response_class=HTMLResponse)
async def parenting_plan_client(request: Request, plan_id: str):
    plan = PARENTING_PLANS.get(plan_id)
    if not plan:
        plan = {
            "id": plan_id,
            "sections": {s: "" for s in PARENTING_PLAN_SECTIONS},
            "status": "sent",
        }
    return templates.TemplateResponse("parenting_plan_client.html", {
        "request": request,
        "plan": plan,
        "sections": PARENTING_PLAN_SECTIONS,
    })


@app.get("/parenting-plan/{plan_id}/generate", response_class=HTMLResponse)
async def parenting_plan_generate(request: Request, plan_id: str):
    plan = PARENTING_PLANS.get(plan_id)
    if not plan:
        plan = {
            "id": plan_id,
            "sections": {s: "" for s in PARENTING_PLAN_SECTIONS},
            "status": "draft",
        }
    return templates.TemplateResponse("parenting_plan_generate.html", {
        "request": request,
        "user": CURRENT_USER,
        "active_tab": "parenting-plan",
        "plan": plan,
        "sections": PARENTING_PLAN_SECTIONS,
    })


@app.get("/health")
async def health():
    return {"status": "ok"}
