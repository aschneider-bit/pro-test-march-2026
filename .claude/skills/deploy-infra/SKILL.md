# /deploy-infra — One-Time EC2 Setup

Provision a shared EC2 instance for hosting vibe code prototypes. Run once per AWS account.

Instances are VPN-protected — no basic auth needed for web access.

Print what you're doing at each step.

## 1. Verify AWS Auth
```bash
aws sts get-caller-identity --profile dev-ai
```
If this fails, tell the user to run `aws sso login --profile dev-ai` and retry.

## 2. Check for Existing Infrastructure
```bash
aws ec2 describe-instances --profile dev-ai --region us-east-2 \
  --filters "Name=tag:Name,Values=vibe-code-host" "Name=instance-state-name,Values=running,stopped" \
  --query "Reservations[].Instances[].[InstanceId,PublicIpAddress,State.Name]" --output text
```
If an instance already exists, print its details (ID, IP, state) and ask the user if they want to proceed or skip.

## 3. Create Security Group
```bash
# Check if it exists first
SG_ID=$(aws ec2 describe-security-groups --profile dev-ai --region us-east-2 \
  --filters "Name=group-name,Values=vibe-code-sg" \
  --query "SecurityGroups[0].GroupId" --output text 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
  SG_ID=$(aws ec2 create-security-group --profile dev-ai --region us-east-2 \
    --group-name vibe-code-sg \
    --description "Vibe Code host - HTTP, HTTPS, SSH" \
    --query "GroupId" --output text)

  aws ec2 authorize-security-group-ingress --profile dev-ai --region us-east-2 \
    --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0
  aws ec2 authorize-security-group-ingress --profile dev-ai --region us-east-2 \
    --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0
  aws ec2 authorize-security-group-ingress --profile dev-ai --region us-east-2 \
    --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0

  aws ec2 create-tags --profile dev-ai --region us-east-2 \
    --resources "$SG_ID" --tags Key=Name,Value=vibe-code-sg
fi
```

## 4. SSH Key Setup
Use the existing `intandem-developer-ai-us-east-2` key pair in AWS. SSH access is provided via user-data that injects `~/.ssh/id_ed25519.pub` into the instance's `authorized_keys`.

If `~/.ssh/id_ed25519.pub` doesn't exist, tell the user to generate a key first with `ssh-keygen -t ed25519`.

## 5. Find Latest Amazon Linux 2023 AMI
```bash
AMI_ID=$(aws ec2 describe-images --profile dev-ai --region us-east-2 \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023.*-x86_64" "Name=state,Values=available" \
  --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" --output text)
```

## 6. Create User-Data Bootstrap Script
Create a script at `/tmp/vibe-userdata.sh` that:
1. Injects the user's `~/.ssh/id_ed25519.pub` into `/home/ec2-user/.ssh/authorized_keys`
2. Installs python3.11, python3.11-pip, nginx, httpd-tools via `dnf`
3. Enables and starts nginx
4. Creates `/opt/apps/` owned by ec2-user with an empty `manifest.json`
5. Replaces `/etc/nginx/nginx.conf` with a clean config that has only `include /etc/nginx/conf.d/*.conf;` inside the http block (no default server block). Do NOT use `sed` to remove the default server block — write the entire file to avoid breaking the config. The http block must be properly closed with `}`.
6. Reloads nginx
7. Touches `/opt/apps/.bootstrap-complete` as a completion signal

## 7. Launch Instance
```bash
INSTANCE_ID=$(aws ec2 run-instances --profile dev-ai --region us-east-2 \
  --image-id "$AMI_ID" \
  --instance-type t3.micro \
  --key-name intandem-developer-ai-us-east-2 \
  --security-group-ids "$SG_ID" \
  --user-data file:///tmp/vibe-userdata.sh \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=vibe-code-host}]" \
  --query "Instances[0].InstanceId" --output text)

aws ec2 wait instance-running --profile dev-ai --region us-east-2 --instance-ids "$INSTANCE_ID"
```

## 8. Get Public IP
No Elastic IP (IAM restriction). Use the auto-assigned public IP instead.
Note: IP may change on instance stop/start.
```bash
PUBLIC_IP=$(aws ec2 describe-instances --profile dev-ai --region us-east-2 \
  --instance-ids "$INSTANCE_ID" \
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text)
```

## 9. Wait for Bootstrap and Verify SSH
Poll for `/opt/apps/.bootstrap-complete` via SSH (retry up to 6 times, 15-second intervals):
```bash
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ec2-user@$PUBLIC_IP \
  "test -f /opt/apps/.bootstrap-complete && echo DONE || echo WAITING"
```

Once done, verify: `python3.11 --version`, `nginx -v`, `which htpasswd`, `cat /opt/apps/manifest.json`, `sudo systemctl is-active nginx`.

## 10. Print Summary
```
========================================
  EC2 Infrastructure Ready
========================================

  Instance:  i-xxxxxxxxx (t3.micro)
  Region:    us-east-2
  Public IP: X.X.X.X
  SSH:       ssh ec2-user@X.X.X.X

  Base URL:  http://<app-name>.X.X.X.X.nip.io
  Auth:      None (VPN-protected)

  Next:      Run /deploy to push your app
========================================
```
Replace placeholders with actual values.
