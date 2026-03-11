# Vibe Code

Rapid web app prototyping. User describes what they want, you build it.

## Stack
Python, FastAPI, uvicorn (hot reload), Jinja2, cloudflared (tunnel), Playwright (screenshots)

## Python Environment
Always use `.venv/`. Run commands with `.venv/bin/python`, `.venv/bin/pip`, `.venv/bin/uvicorn`.

## First Session
If `main.py` doesn't exist, run `/setup` before anything else. It handles git, venv, deps, and starter files.

## Skills
- `/setup` — First-time project initialization (run once, creates everything)
- `/vibe` — Start server + public tunnel + screenshot verification

## Workflow
**edit → auto-commit → hot-reload → verify**
1. Edit files normally — the auto-commit hook (`.claude/hooks/auto-commit.sh`) stages and commits after every Edit/Write
2. uvicorn `--reload` picks up changes instantly
3. After significant changes, screenshot with Playwright to verify

## File Layout
| Path | Purpose |
|------|---------|
| `main.py` | FastAPI entry point (routes, auth middleware, logging) |
| `templates/base.html` | HTML layout (`{% block content %}`) |
| `templates/*.html` | Page templates extending base |
| `static/` | CSS, JS, images (served at `/static/`) |
| `requirements.txt` | Python deps |

## Logging
- Routes use Python `logging` module, never `print()`
- Server logs: `/tmp/uvicorn.log`
- Tunnel logs: `/tmp/cloudflared.log`
- Always tell the user what you're doing — no silent operations

## Debugging
On errors: read `/tmp/uvicorn.log` → screenshot the error page → diagnose → fix → re-screenshot to confirm

## Screenshots
Take Playwright screenshots after: new/modified routes, template/style edits, error fixes, or when user asks.
```bash
.venv/bin/python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.goto('http://localhost:8000')
    page.wait_for_load_state('networkidle')
    page.screenshot(path='/tmp/screenshot.png')
    browser.close()
"
```
Read `/tmp/screenshot.png` and describe what you see.

## Auth
Tunnel protected with basic auth (default `demo`/`demo`). Localhost bypasses auth.

## Git
- Auto-commits via hook: `auto: update <filename>`
- Manual milestone commits at logical points: `git add -A && git commit -m "feat: description"`
- Prefixes: `feat:`, `fix:`, `refactor:`, `style:`, `docs:`

## Rollback
```bash
git log --oneline -10                        # history
git diff <hash>^ <hash>                      # inspect commit
git reset --soft HEAD~1                      # undo last commit
git checkout <hash> -- <file>                # restore file
```
Always explain rollbacks to the user before executing.

## EC2 Deployment

Deploy prototypes to a shared EC2 instance for persistent hosting. Multiple apps share one t3.micro via Nginx reverse proxy, accessible at `http://<app>.X.X.X.X.nip.io`.

### Skills
- `/deploy-infra` — One-time EC2 setup (instance, security group, Elastic IP, bootstrap)
- `/deploy` — Deploy current project to EC2 (rsync, systemd, nginx, basic auth)
- `/status` — Show instance info, deployed apps, service health, disk/memory
- `/teardown` — Remove a single app or destroy all infrastructure
- `/check` — Quick overview of all AWS resources and deployed apps (no SSH needed if instance is down)

### How It Works
- **Nginx** reverse proxy on port 80, per-app server blocks routing `<app>.IP.nip.io` to `127.0.0.1:<port>`
- **nip.io** provides wildcard DNS: `app.1.2.3.4.nip.io` resolves to `1.2.3.4`
- **systemd** service per app (`vibe-<app>.service`) with auto-restart
- **manifest.json** at `/opt/apps/manifest.json` tracks all deployed apps, ports, and metadata
- Apps bind to `127.0.0.1` only (no direct port access from internet)
- No basic auth on EC2 — instances are VPN-protected
- SSH via user-data key injection (uses `~/.ssh/id_ed25519.pub`), key pair `intandem-developer-ai-us-east-2`
- No Elastic IP (IAM restriction) — public IP may change on instance stop/start

### AWS
- Profile: `dev-ai` (us-east-2)
- Re-login: `aws sso login --profile dev-ai`
- Resources tagged: `vibe-code-host`, `vibe-code-eip`, `vibe-code-sg`, `vibe-code-key`
