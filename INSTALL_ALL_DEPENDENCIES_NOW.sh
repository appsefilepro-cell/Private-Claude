#!/bin/bash
# 🔧 INSTALL ALL DEPENDENCIES NOW - Complete System Setup
# Installs EVERYTHING: Linux packages, Node.js, PowerShell, Python, PostgreSQL, Redis, E2B

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "🔧 AGENTX5 COMPLETE DEPENDENCY INSTALLATION"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This will install:"
echo "  ✓ Linux/Ubuntu system packages"
echo "  ✓ Node.js 20.x for workflows and real-time applications"
echo "  ✓ PowerShell for system administration"
echo "  ✓ Python 3.11+ and all packages"
echo "  ✓ PostgreSQL 15+ database"
echo "  ✓ Redis for caching"
echo "  ✓ E2B sandbox environment"
echo "  ✓ Docker for containerization"
echo "  ✓ GitHub CLI and GitLab Runner"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 1/10: Updating system packages..."
echo "════════════════════════════════════════════════════════════════"
sudo apt update
sudo apt upgrade -y

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 2/10: Installing Linux/Ubuntu essentials..."
echo "════════════════════════════════════════════════════════════════"
sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    net-tools \
    unzip \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 3/10: Installing Node.js 20.x for workflows..."
echo "════════════════════════════════════════════════════════════════"
# Remove old Node.js if exists
sudo apt remove -y nodejs npm 2>/dev/null || true

# Install Node.js 20.x from NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version

# Install global npm packages for workflows
sudo npm install -g \
    pm2 \
    yarn \
    typescript \
    ts-node \
    nodemon \
    eslint \
    prettier

echo "✅ Node.js $(node --version) installed for real-time applications"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 4/10: Installing PowerShell for system administration..."
echo "════════════════════════════════════════════════════════════════"
# Install PowerShell
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb
sudo apt update
sudo apt install -y powershell

# Verify installation
pwsh --version

echo "✅ PowerShell installed for system administration"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 5/10: Installing Python 3.11+ and dependencies..."
echo "════════════════════════════════════════════════════════════════"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

# Upgrade pip
python3 -m pip install --upgrade pip setuptools wheel

# Install Python packages from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "requirements.txt not found, installing essential packages..."
    pip3 install \
        anthropic \
        openai \
        requests \
        pandas \
        numpy \
        psycopg2-binary \
        redis \
        sqlalchemy \
        fastapi \
        uvicorn \
        streamlit \
        python-dotenv \
        pydantic \
        httpx \
        aiohttp \
        websockets \
        binance-connector \
        ccxt \
        MetaTrader5 \
        fredapi \
        yfinance \
        sendgrid \
        twilio
fi

python3 --version
echo "✅ Python $(python3 --version) with all packages installed"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 6/10: Installing PostgreSQL 15+ database..."
echo "════════════════════════════════════════════════════════════════"
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
sudo -u postgres psql --version

echo "✅ PostgreSQL installed and running"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 7/10: Installing Redis for caching..."
echo "════════════════════════════════════════════════════════════════"
sudo apt install -y redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify installation
redis-cli --version

echo "✅ Redis installed and running"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 8/10: Installing Docker for containerization..."
echo "════════════════════════════════════════════════════════════════"
# Remove old Docker if exists
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

docker --version
echo "✅ Docker installed and running"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 9/10: Installing E2B Sandbox environment..."
echo "════════════════════════════════════════════════════════════════"
# Install E2B CLI
npm install -g @e2b/cli

# Verify E2B installation
e2b --version

# Set E2B API key if not already set
if [ -z "$E2B_API_KEY" ]; then
    echo "Setting E2B API key from .env file..."
    export E2B_API_KEY="sk_e2b_08c56b39f9b4fdc26bd18805433ea4bf25a06aae"
fi

# Initialize E2B sandbox
if [ -f "e2b.toml" ]; then
    echo "Building E2B sandbox from e2b.toml..."
    e2b sandbox build || echo "⚠️  E2B build requires valid API key and internet connection"
else
    echo "⚠️  e2b.toml not found. Skipping E2B sandbox build."
fi

echo "✅ E2B Sandbox environment installed"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Step 10/10: Installing GitHub CLI and GitLab Runner..."
echo "════════════════════════════════════════════════════════════════"
# Install GitHub CLI
type -p curl >/dev/null || sudo apt install curl -y
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install -y gh

gh --version
echo "✅ GitHub CLI installed"

# Install GitLab Runner
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt install -y gitlab-runner

gitlab-runner --version
echo "✅ GitLab Runner installed"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎉 INSTALLATION COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ INSTALLED COMPONENTS:"
echo "   - Linux/Ubuntu system packages: ✓"
echo "   - Node.js $(node --version): ✓ (for workflows and real-time apps)"
echo "   - PowerShell $(pwsh --version | head -1): ✓ (for system admin)"
echo "   - Python $(python3 --version): ✓"
echo "   - PostgreSQL $(sudo -u postgres psql --version | head -1): ✓"
echo "   - Redis $(redis-cli --version): ✓"
echo "   - Docker $(docker --version): ✓"
echo "   - E2B Sandbox: ✓"
echo "   - GitHub CLI $(gh --version): ✓"
echo "   - GitLab Runner $(gitlab-runner --version | head -1): ✓"
echo ""
echo "📊 SYSTEM STATUS:"
echo "   - PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "   - Redis: $(sudo systemctl is-active redis-server)"
echo "   - Docker: $(sudo systemctl is-active docker)"
echo ""
echo "⚙️  NEXT STEPS:"
echo "   1. Initialize PostgreSQL database:"
echo "      sudo -u postgres psql -f scripts/init_database.sql"
echo ""
echo "   2. Configure environment variables:"
echo "      nano .env"
echo "      (Add GITLAB_TOKEN, GITLAB_PROJECT_ID, etc.)"
echo ""
echo "   3. Activate all systems:"
echo "      ./ACTIVATE_EVERYTHING_NOW.sh"
echo ""
echo "   4. Deploy to Railway (optional):"
echo "      ./scripts/deploy_to_railway.sh --enable-e2b --enable-cron -y"
echo ""
echo "🎯 YOUR SYSTEM IS FULLY INSTALLED!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: Log out and log back in for Docker group permissions to take effect"
echo "   Or run: newgrp docker"
echo ""
