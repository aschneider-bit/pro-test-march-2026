# Vibe Code

AI-powered rapid web app prototyping. Describe what you want, Claude builds it. Every change is auto-versioned, hot-reloaded, and verifiable via screenshot — locally or deployed to EC2.

## How It Works

```
You describe an idea
        ↓
Claude edits files → auto-committed to git → hot-reloaded by uvicorn
        ↓
Playwright screenshots verify the result
        ↓
Share via cloudflared tunnel (temporary) or EC2 deploy (persistent)
```

## Quick Start

1. Open Claude Code in a new project directory
2. Say `/setup` — creates git repo, virtual environment, dependencies, and starter files
3. Describe what you want to build
4. Say `/vibe` — starts the server and gives you a public URL

## Stack

| Tool | Purpose |
|------|---------|
| **Python + FastAPI** | Backend framework with async support |
| **uvicorn** | ASGI server with `--reload` for instant hot-reloading |
| **Jinja2** | HTML templating with `{% block %}` inheritance |
| **Playwright** | Headless Chromium screenshots for visual verification |
| **cloudflared** | Temporary public HTTPS tunnels (no account needed) |
| **Git + hooks** | Auto-versioning — every file edit creates a commit |
| **AWS EC2 + Nginx** | Persistent hosting with per-app reverse proxy |

## Skills (Slash Commands)

### Local Development

#### `/setup`
First-time project initialization. Run once when starting a new project.

- Initializes a git repository
- Creates `.venv/` Python virtual environment
- Installs FastAPI, uvicorn, Jinja2, Playwright
- Installs system tools (jq, cloudflared) via Homebrew
- Creates starter files: `main.py`, templates, static CSS, `.gitignore`, `requirements.txt`
- Makes the auto-commit hook executable
- Creates an initial git commit

#### `/vibe`
Start the dev server and open a public tunnel for sharing.

- Checks and installs any missing dependencies
- Kills any stale processes on port 8000
- Starts uvicorn with `--reload` on `0.0.0.0:8000`
- Starts a cloudflared tunnel for a public HTTPS URL
- Takes a Playwright screenshot to verify the app renders correctly
- Prints the local URL, public URL, and auth credentials (`demo`/`demo`)

### EC2 Deployment

#### `/deploy-infra`
One-time setup of the shared EC2 instance. Run once per AWS account.

- Verifies AWS SSO auth (`dev-ai` profile, `us-east-2`)
- Creates security group `vibe-code-sg` (ports 22, 80, 443)
- Finds the latest Amazon Linux 2023 AMI
- Launches a `t3.micro` instance with user-data bootstrap
- Bootstrap installs: Python 3.11, Nginx, httpd-tools
- Creates `/opt/apps/manifest.json` to track deployed apps
- Injects your SSH key (`~/.ssh/id_ed25519.pub`) for access

#### `/deploy`
Deploy the current project to EC2. Run from any project directory.

- Derives app name from directory name (lowercase, hyphenated)
- Looks up the running `vibe-code-host` instance
- Assigns a port (8001+, sequential, reuses on redeploy)
- `rsync`s project files (excludes `.venv`, `.git`, `.claude`, `__pycache__`)
- Creates a Python venv on EC2 and installs `requirements.txt`
- Creates a systemd service (`vibe-<app>.service`) with auto-restart
- Creates an Nginx reverse proxy config (`<app>.<ip>.nip.io` -> `127.0.0.1:<port>`)
- Updates the manifest and verifies with a health check curl
- URL pattern: `http://<app-name>.<ip>.nip.io`

#### `/status`
Dashboard view of the EC2 instance and all deployed apps.

- Shows instance ID, type, state, IP, launch time
- Lists all deployed apps with port, URL, and systemd status (active/inactive/failed)
- Shows disk and memory usage

#### `/check`
Quick AWS resource inventory. Works even when the instance is down.

- Lists all `vibe-code-host` instances (any state)
- Lists security groups
- If a running instance exists, SSHs in to show deployed apps and their health
- No SSH required when instance is terminated — just shows AWS resources

#### `/teardown`
Remove apps or destroy infrastructure.

- `/teardown` — Interactive: shows deployed apps, asks what to remove
- `/teardown <app-name>` — Removes one app: stops service, deletes nginx config, removes directory, updates manifest
- `/teardown --all` — Destroys everything: terminates instance, deletes security group (asks for confirmation)

## Auto-Versioning

Every file edit is automatically committed to git via a post-tool hook:

```
You ask Claude to change something
        ↓
Claude edits a file (Edit or Write tool)
        ↓
Hook fires: stages file + tracked changes → git commit "auto: update <filename>"
        ↓
Full history preserved — rollback to any point
```

The hook runs asynchronously and never blocks Claude. Commits use `--no-verify` to avoid pre-commit hook delays.

**Rollback commands:**
```bash
git log --oneline -10              # see recent history
git diff <hash>^ <hash>            # inspect a specific commit
git reset --soft HEAD~1            # undo last commit (keeps changes)
git checkout <hash> -- <file>      # restore a single file
```

**Milestone commits** are created manually at logical points using conventional prefixes: `feat:`, `fix:`, `refactor:`, `style:`, `docs:`

## Visual Verification (Playwright)

After significant changes, Claude takes a headless Chromium screenshot and describes what it sees. This catches rendering issues, broken layouts, and errors that wouldn't show up in logs.

Screenshots are taken after:
- New or modified routes
- Template or style edits
- Error fixes (before and after)
- When you ask

Screenshot output: `/tmp/screenshot.png`

## Project Structure

```
my-project/
├── .claude/
│   ├── hooks/
│   │   └── auto-commit.sh        # Auto-versioning hook
│   ├── skills/
│   │   ├── setup/SKILL.md        # /setup skill definition
│   │   ├── vibe/SKILL.md         # /vibe skill definition
│   │   ├── deploy-infra/SKILL.md # /deploy-infra skill definition
│   │   ├── deploy/SKILL.md       # /deploy skill definition
│   │   ├── status/SKILL.md       # /status skill definition
│   │   ├── check/SKILL.md        # /check skill definition
│   │   └── teardown/SKILL.md     # /teardown skill definition
│   └── settings.local.json       # Permissions and hook config
├── templates/
│   ├── base.html                 # Layout template
│   └── *.html                    # Page templates
├── static/
│   └── style.css                 # Styles
├── main.py                       # FastAPI app (routes, middleware)
├── requirements.txt              # Python dependencies
├── CLAUDE.md                     # AI instructions
└── README.md                     # This file
```

## EC2 Architecture

```
Local Machine                         EC2 t3.micro (us-east-2)
┌──────────┐    rsync + ssh           ┌─────────────────────────┐
│ main.py  │ ──────────────────────>  │ /opt/apps/<app-name>/   │
│ templates/│                         │   .venv/, main.py, ...  │
│ static/  │                         │                         │
└──────────┘                         │ Nginx :80               │
                                     │  app1.IP.nip.io → :8001 │
                                     │  app2.IP.nip.io → :8002 │
                                     │                         │
                                     │ systemd per app         │
                                     │ /opt/apps/manifest.json │
                                     └─────────────────────────┘
```

- **Nginx** reverse proxy routes `<app>.IP.nip.io` to the correct localhost port
- **nip.io** provides free wildcard DNS: `app.1.2.3.4.nip.io` resolves to `1.2.3.4`
- **systemd** manages each app as a service with auto-restart on crash
- **manifest.json** is the single source of truth for deployed apps, ports, and metadata
- Apps bind to `127.0.0.1` only — accessible exclusively through Nginx
- Instances are VPN-protected — no basic auth needed on EC2

## AWS Details

| Setting | Value |
|---------|-------|
| Profile | `dev-ai` |
| Region | `us-east-2` |
| Instance type | `t3.micro` (~$7.50/mo) |
| Key pair | `intandem-developer-ai-us-east-2` |
| SSH access | User-data injects `~/.ssh/id_ed25519.pub` |
| Re-login | `aws sso login --profile dev-ai` |

Resource tags: `vibe-code-host` (instance), `vibe-code-sg` (security group)

## Logs

| Log | Location |
|-----|----------|
| Local server | `/tmp/uvicorn.log` |
| Local tunnel | `/tmp/cloudflared.log` |
| EC2 app logs | `ssh ec2-user@<ip> "sudo journalctl -u vibe-<app> -f"` |
| EC2 nginx | `ssh ec2-user@<ip> "sudo tail -f /var/log/nginx/error.log"` |
| Screenshots | `/tmp/screenshot.png` |
