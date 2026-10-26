#!/bin/bash
# ==============================================================================
# AWS EC2 Continuous Deployment / Quick Update Script
# Updates code, dependencies, restarts services, and verifies health.
# Usage:
#   bash scripts/deploy_ec2.sh
# ==============================================================================

set -e

PROJECT_DIR="/home/ubuntu/bda-project"
cd "$PROJECT_DIR"

echo "🔄 [1/4] Pulling latest updates..."
if [ -d ".git" ]; then
    git pull origin main || echo "Git pull skipped (working directory dirty or not tracked)"
fi

echo "📦 [2/4] Updating Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo "⚙️ [3/4] Restarting services..."
sudo systemctl restart mongod || true
sudo systemctl restart sparkrec.service
sudo systemctl reload nginx

echo "🔍 [4/4] Verifying health..."
sleep 3
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health || echo "FAILED")

if [ "$HEALTH_CODE" = "200" ]; then
    echo "✅ Application is HEALTHY (HTTP 200)!"
    curl -s http://localhost/api/health | python3 -m json.tool
else
    echo "❌ Health check failed with status: $HEALTH_CODE"
    echo "Checking logs:"
    sudo journalctl -u sparkrec.service -n 20 --no-pager
    exit 1
fi

echo "🚀 Deployment successfully completed!"
