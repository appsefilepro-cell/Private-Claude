#!/bin/bash
# Google CLI Setup Script for AgentX5

echo "🚀 Setting up Google CLI (gcloud)..."

# Install gcloud CLI (if not installed)
if ! command -v gcloud &> /dev/null; then
    echo "📦 Installing gcloud CLI..."
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
fi

# Initialize gcloud
echo "🔧 Initializing gcloud..."
gcloud init --skip-diagnostics

# Set project
echo "📊 Setting project..."
gcloud config set project agentx5-project

# Authenticate with service account (if key file exists)
if [ -f "agentx5-service-account-key.json" ]; then
    echo "🔑 Authenticating with service account..."
    gcloud auth activate-service-account --key-file=agentx5-service-account-key.json
fi

echo "✅ Google CLI setup complete!"
