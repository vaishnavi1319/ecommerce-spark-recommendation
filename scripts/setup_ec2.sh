#!/bin/bash
# ==============================================================================
# AWS EC2 Automated Provisioning Script
# E-Commerce Product Recommendation Using Apache Spark
# Target OS: Ubuntu 22.04 LTS / 24.04 LTS (x86_64)
# ==============================================================================
# This script configures a fresh EC2 instance with:
#   1. System packages & build dependencies
#   2. OpenJDK 17 (Java runtime for Apache Spark & PySpark)
#   3. Python 3, pip, and virtual environment
#   4. MongoDB 7.0 Community Edition
#   5. Application dependencies from requirements.txt
#   6. Systemd service (sparkrec.service) for automatic startup & recovery
#   7. Nginx reverse proxy (Port 80 -> Port 5000)
#   8. UFW firewall rules
# ==============================================================================

set -e  # Exit immediately if a command fails

echo "============================================================"
echo "🚀 Starting SparkRec EC2 Setup Pipeline..."
echo "============================================================"

PROJECT_DIR="/home/ubuntu/bda-project"
USER_NAME="ubuntu"

# ── 1. System Updates & Essential Packages ────────────────────
echo "📦 [1/8] Updating apt repositories and installing base utilities..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    ufw \
    nginx

# ── 2. OpenJDK 17 (Required for PySpark) ──────────────────────
echo "☕ [2/8] Installing OpenJDK 17 for Apache Spark..."
sudo apt-get install -y openjdk-17-jdk-headless

JAVA_PATH=$(dirname $(dirname $(readlink -f $(which java))))
echo "Java detected at: $JAVA_PATH"

# Persist JAVA_HOME globally
if ! grep -q "JAVA_HOME" /etc/environment; then
    echo "JAVA_HOME=\"$JAVA_PATH\"" | sudo tee -a /etc/environment
fi
export JAVA_HOME="$JAVA_PATH"

# ── 3. Python 3 & Virtual Environment Tools ───────────────────
echo "🐍 [3/8] Installing Python 3 & pip..."
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# ── 4. MongoDB Community Edition Installation ─────────────────
echo "🍃 [4/8] Installing MongoDB Community Edition..."
if ! command -v mongod &> /dev/null; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor --yes
    
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
        sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

    sudo apt-get update -y
    sudo apt-get install -y mongodb-org || sudo apt-get install -y mongodb
fi

# Enable and start MongoDB
sudo systemctl daemon-reload
sudo systemctl enable mongod || sudo systemctl enable mongodb
sudo systemctl start mongod || sudo systemctl start mongodb

echo "MongoDB status:"
sudo systemctl is-active mongod || sudo systemctl is-active mongodb

# ── 5. Project Directory & Python Environment ─────────────────
echo "📁 [5/8] Setting up Python virtual environment..."
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install gunicorn

# Ensure .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    # Adjust JAVA_HOME for Ubuntu
    sed -i "s|JAVA_HOME=.*|JAVA_HOME=$JAVA_PATH|g" .env
fi

# Ensure data directories exist
mkdir -p data/raw data/processed data/mongodb

# Generate initial dataset if raw CSV doesn't exist
if [ ! -f "data/raw/ecommerce_interactions.csv" ]; then
    echo "Generating base e-commerce dataset..."
    python3 scripts/generate_large_dataset.py --interactions 10000 --output data/raw/ecommerce_interactions.csv
fi

# ── 6. Systemd Service Configuration ──────────────────────────
echo "⚙️ [6/8] Configuring systemd service (sparkrec.service)..."
sudo cp scripts/sparkrec.service /etc/systemd/system/sparkrec.service
sudo sed -i "s|/home/ubuntu/bda-project|$PROJECT_DIR|g" /etc/systemd/system/sparkrec.service
sudo sed -i "s|User=ubuntu|User=$USER_NAME|g" /etc/systemd/system/sparkrec.service

sudo systemctl daemon-reload
sudo systemctl enable sparkrec.service
sudo systemctl restart sparkrec.service

# ── 7. Nginx Reverse Proxy Configuration ──────────────────────
echo "🌐 [7/8] Configuring Nginx reverse proxy..."
sudo cp scripts/nginx_sparkrec.conf /etc/nginx/sites-available/sparkrec.conf
sudo ln -sf /etc/nginx/sites-available/sparkrec.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl restart nginx

# ── 8. Firewall Configuration ─────────────────────────────────
echo "🛡️ [8/8] Configuring UFW firewall..."
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP (Nginx)'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 5000/tcp comment 'Flask Direct (Optional)'
sudo ufw --force enable || true

echo "============================================================"
echo "🎉 EC2 Deployment & Provisioning Complete!"
echo "============================================================"
echo "Service Status:"
sudo systemctl status sparkrec.service --no-pager -l || true
echo ""
echo "Verify application:"
echo "  curl http://localhost/api/health"
echo "  curl http://localhost/api/analytics/public"
echo "============================================================"
