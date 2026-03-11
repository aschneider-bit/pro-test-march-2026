# /check — Quick AWS Resource and App Check

Fast overview of all vibe-code resources and deployed apps. No SSH required if the instance is down.

Print results as you go.

## 1. Verify AWS Auth
```bash
aws sts get-caller-identity --profile dev-ai --query "Account" --output text
```
If this fails, tell the user to run `aws sso login --profile dev-ai`.

## 2. Check EC2 Instances
```bash
aws ec2 describe-instances --profile dev-ai --region us-east-2 \
  --filters "Name=tag:Name,Values=vibe-code-host" \
  --query "Reservations[].Instances[].[InstanceId,InstanceType,State.Name,PublicIpAddress,LaunchTime]" --output table
```
If no instances found (or all terminated), print "No vibe-code instances found."

## 3. Check Security Groups
```bash
aws ec2 describe-security-groups --profile dev-ai --region us-east-2 \
  --filters "Name=group-name,Values=vibe-code-sg" \
  --query "SecurityGroups[].[GroupId,GroupName]" --output table
```

## 4. Check Deployed Apps (if instance is running)
If a running instance was found in step 2, SSH in and read the manifest:
```bash
ssh -o ConnectTimeout=5 -o BatchMode=yes ec2-user@$PUBLIC_IP "cat /opt/apps/manifest.json" 2>/dev/null
```
For each app in the manifest, also check its systemd service status:
```bash
ssh ec2-user@$PUBLIC_IP "sudo systemctl is-active vibe-<app-name>" 2>/dev/null
```

If SSH fails or no running instance, skip this step and note "Instance not reachable — cannot check deployed apps."

## 5. Print Summary
```
========================================
  Vibe Code — AWS Resources (dev-ai)
========================================

  EC2 Instances:
    i-xxxx  t3.micro  running  18.x.x.x  (launched 2026-03-11)
    — or "None found"

  Security Groups:
    sg-xxxx  vibe-code-sg
    — or "None found"

  Deployed Apps:
  ┌────────────┬──────┬──────────────────────────────────────┬────────┐
  │ App        │ Port │ URL                                  │ Status │
  ├────────────┼──────┼──────────────────────────────────────┼────────┤
  │ my-app     │ 8001 │ http://my-app.x.x.x.x.nip.io       │ active │
  └────────────┴──────┴──────────────────────────────────────┴────────┘
    — or "No apps deployed" / "Instance not reachable"

========================================
```
Replace placeholders with actual values.
