# Vibe Code

Rapid web app prototyping. User describes what they want, you build it.

## Environment
- Python venv: `.venv/bin/python`, `.venv/bin/pip`, `.venv/bin/uvicorn`
- Logs: `/tmp/uvicorn.log`, `/tmp/cloudflared.log`
- Screenshots: `/tmp/screenshot.png`
- Use `logging` module, never `print()`

## Skills
| Command | When to use |
|---------|------------|
| `/setup` | No `main.py` exists — first-time init (git, venv, deps, starter files) |
| `/vibe` | Start local server + cloudflared tunnel + screenshot verify |
| `/deploy-infra` | One-time EC2 setup (first deploy ever) |
| `/deploy` | Push current project to EC2 for persistent hosting |
| `/status` | Check EC2 instance, deployed apps, service health, disk/memory |
| `/check` | Quick AWS resource inventory (works even if instance is down) |
| `/teardown` | Remove an app or destroy all EC2 infrastructure |

## Workflow
**edit -> auto-commit -> hot-reload -> verify**
1. Edit files — hook auto-commits after every Edit/Write (`auto: update <filename>`)
2. uvicorn `--reload` picks up changes instantly
3. Screenshot with Playwright after significant changes to verify visually

## Playwright Screenshots
Take after: new/modified routes, template/style edits, error fixes, or when asked.
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

## Debugging
Read `/tmp/uvicorn.log` -> screenshot the error page -> diagnose -> fix -> re-screenshot to confirm.

## Git
- Auto-commits via hook (async, never blocks)
- Milestone commits: `git add -A && git commit -m "feat: description"`
- Prefixes: `feat:`, `fix:`, `refactor:`, `style:`, `docs:`
- Rollback: `git log --oneline -10`, `git reset --soft HEAD~1`, `git checkout <hash> -- <file>`
- Always explain rollbacks before executing

## File Layout
`main.py` (FastAPI app) | `templates/base.html` + `templates/*.html` | `static/` | `requirements.txt`

## Auth
- Tunnel: basic auth `demo`/`demo` (localhost bypasses)
- EC2: no auth needed (VPN-protected)

## EC2 Deployment
- AWS profile `dev-ai`, region `us-east-2`, key pair `intandem-developer-ai-us-east-2`
- SSH via user-data key injection (`~/.ssh/id_ed25519.pub`)
- No Elastic IP — public IP may change on instance stop/start
- Re-login: `aws sso login --profile dev-ai`
- Nginx reverse proxy, systemd services, manifest at `/opt/apps/manifest.json`
- URL pattern: `http://<app-name>.<ip>.nip.io`
