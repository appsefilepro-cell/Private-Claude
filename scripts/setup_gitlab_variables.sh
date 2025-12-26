#!/bin/bash

# ============================================================================
# GitLab CI/CD Variables Setup Script
# Automates adding API keys to GitLab project variables
# ============================================================================

set -e

echo "🔐 GitLab CI/CD Variables Setup Script"
echo "======================================="
echo ""

# GitLab Configuration (UPDATE THESE)
GITLAB_URL="https://gitlab.com"
GITLAB_PROJECT_ID="${GITLAB_PROJECT_ID:-}"  # Set this in .env or environment
GITLAB_TOKEN="${GITLAB_TOKEN:-}"  # Set this in .env or environment

# Check if project ID is set
if [ -z "$GITLAB_PROJECT_ID" ]; then
    echo "❌ GITLAB_PROJECT_ID not set"
    echo "Please set it in your .env file or export it:"
    echo "   export GITLAB_PROJECT_ID=your_project_id"
    exit 1
fi

# Check if token is set
if [ -z "$GITLAB_TOKEN" ]; then
    echo "❌ GITLAB_TOKEN not set"
    echo "Please create a personal access token with 'api' scope at:"
    echo "   $GITLAB_URL/-/profile/personal_access_tokens"
    echo "Then set it in your .env file or export it:"
    echo "   export GITLAB_TOKEN=your_token"
    exit 1
fi

echo "✅ GitLab configuration loaded"
echo "   Project ID: $GITLAB_PROJECT_ID"
echo ""

# ============================================================================
# Load API keys from .env file
# ============================================================================

ENV_FILE="/home/user/Private-Claude/.env"

if [ -f "$ENV_FILE" ]; then
    echo "📂 Loading API keys from $ENV_FILE"
    source "$ENV_FILE"
    echo "✅ Environment file loaded"
    echo ""
else
    echo "⚠️  Warning: .env file not found at $ENV_FILE"
    echo "   You'll need to enter variables manually"
    echo ""
fi

# ============================================================================
# Function to add or update GitLab CI/CD variable
# ============================================================================

add_gitlab_variable() {
    local key=$1
    local value=$2
    local protected=${3:-true}
    local masked=${4:-true}
    local description=$5

    echo "📝 Adding variable: $key"
    echo "   Description: $description"
    echo "   Protected: $protected | Masked: $masked"

    if [ -z "$value" ]; then
        echo "⚠️  Skipping $key (value not provided)"
        echo ""
        return
    fi

    # Create JSON payload
    local json_payload=$(cat <<EOF
{
  "key": "$key",
  "value": "$value",
  "protected": $protected,
  "masked": $masked,
  "variable_type": "env_var"
}
EOF
)

    # Check if variable exists
    local existing_var=$(curl --silent --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        "$GITLAB_URL/api/v4/projects/$GITLAB_PROJECT_ID/variables/$key")

    if echo "$existing_var" | grep -q '"key"'; then
        # Update existing variable
        response=$(curl --silent --request PUT \
            --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
            --header "Content-Type: application/json" \
            --data "$json_payload" \
            "$GITLAB_URL/api/v4/projects/$GITLAB_PROJECT_ID/variables/$key")

        if echo "$response" | grep -q '"key"'; then
            echo "✅ Updated $key"
        else
            echo "❌ Failed to update $key"
            echo "   Response: $response"
        fi
    else
        # Create new variable
        response=$(curl --silent --request POST \
            --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
            --header "Content-Type: application/json" \
            --data "$json_payload" \
            "$GITLAB_URL/api/v4/projects/$GITLAB_PROJECT_ID/variables")

        if echo "$response" | grep -q '"key"'; then
            echo "✅ Created $key"
        else
            echo "❌ Failed to create $key"
            echo "   Response: $response"
        fi
    fi
    echo ""
}

# ============================================================================
# Add variables to GitLab
# ============================================================================

echo "🚀 Adding CI/CD variables to GitLab..."
echo ""

# AI Provider API Keys
add_gitlab_variable "OPENAI_API_KEY" "$OPENAI_API_KEY" true true \
    "OpenAI API key for code generation"

add_gitlab_variable "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY" true true \
    "Anthropic Claude API key for legal analysis"

add_gitlab_variable "GEMINI_API_KEY" "$GEMINI_API_KEY" true true \
    "Google Gemini API key (FREE tier)"

# Infrastructure Keys
add_gitlab_variable "E2B_API_KEY" "$E2B_API_KEY" true true \
    "E2B Sandbox API key"

add_gitlab_variable "E2B_WEBHOOK_ID" "$E2B_WEBHOOK_ID" false false \
    "E2B Webhook ID"

add_gitlab_variable "POSTMAN_API_KEY" "$POSTMAN_API_KEY" true true \
    "Postman API key"

# Integration Webhooks (not masked - URLs)
add_gitlab_variable "ZAPIER_WEBHOOK_URL" "$ZAPIER_WEBHOOK_URL" true false \
    "Zapier webhook URL for automation"

add_gitlab_variable "SLACK_WEBHOOK" "$SLACK_WEBHOOK" true false \
    "Slack webhook for notifications"

# Trading API Keys (if configured)
if [ -n "$OKX_API_KEY" ]; then
    add_gitlab_variable "OKX_API_KEY" "$OKX_API_KEY" true true \
        "OKX trading API key"

    add_gitlab_variable "OKX_SECRET_KEY" "$OKX_SECRET_KEY" true true \
        "OKX trading secret key"

    add_gitlab_variable "OKX_PASSPHRASE" "$OKX_PASSPHRASE" true true \
        "OKX trading passphrase"
fi

# GitHub Integration (for bidirectional sync)
if [ -n "$GITHUB_TOKEN" ]; then
    add_gitlab_variable "GITHUB_TOKEN" "$GITHUB_TOKEN" true true \
        "GitHub personal access token"

    add_gitlab_variable "GITHUB_REPO" "$GITHUB_REPO" false false \
        "GitHub repository path"
fi

# ============================================================================
# Verify variables were added
# ============================================================================

echo "📋 Verifying variables..."
echo ""

curl --silent --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$GITLAB_PROJECT_ID/variables" | \
    python3 -m json.tool

echo ""
echo "✅ GitLab CI/CD Variables setup complete!"
echo ""
echo "📝 Note: Masked variable values are hidden. To update a variable, run this script again."
echo ""
echo "🔍 To test variables in a pipeline, commit and push changes to trigger CI/CD"
echo ""
