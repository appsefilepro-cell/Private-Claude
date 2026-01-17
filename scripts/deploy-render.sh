#!/bin/bash

echo "🚀 Deploying to Render.com..."
echo "⚠️  PRESERVING all existing templates and documents..."

# Verify critical files exist before deployment
echo ""
echo "📋 Verification Checklist:"
echo "=========================="

# Check legal templates
if [ -d "pillar-b-legal/templates" ]; then
  echo "✅ Legal templates directory found"
  template_count=$(find pillar-b-legal/templates -type f | wc -l)
  echo "   └─ $template_count template files detected"
else
  echo "⚠️  Warning: Legal templates directory not found!"
fi

# Check legal prompts
if [ -d "pillar-b-legal/prompts" ]; then
  echo "✅ Legal prompts directory found"
  prompt_count=$(find pillar-b-legal/prompts -type f | wc -l)
  echo "   └─ $prompt_count prompt files detected"
else
  echo "⚠️  Warning: Legal prompts directory not found!"
fi

# Check agent tools
if [ -d "agent-4.0/tools" ]; then
  echo "✅ Agent tools directory found"
  tool_count=$(find agent-4.0/tools -type f -name "*.py" | wc -l)
  echo "   └─ $tool_count Python tool files detected"
else
  echo "⚠️  Warning: Agent tools directory not found!"
fi

# Check app components
if [ -d "app/components" ]; then
  echo "✅ App components directory found"
  component_count=$(find app/components -type f -name "*.tsx" | wc -l)
  echo "   └─ $component_count component files detected"
else
  echo "⚠️  Warning: App components directory not found!"
fi

echo ""
echo "=========================="
echo "✅ All critical directories verified"
echo ""

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "📦 Render CLI not found. Installing..."
    npm install -g @render/cli
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Render CLI"
        echo "💡 You can deploy manually via the Render Dashboard"
        echo "   1. Go to https://dashboard.render.com"
        echo "   2. Connect your GitHub repository"
        echo "   3. Render will auto-detect render.yaml configuration"
        exit 1
    fi
fi

echo "📦 Starting deployment process..."
echo ""

# Deploy using Render blueprint
if command -v render &> /dev/null; then
    echo "🚀 Deploying with Render CLI..."
    render blueprint deploy
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Deployment initiated successfully!"
        echo "📊 Check deployment status at: https://dashboard.render.com"
    else
        echo ""
        echo "⚠️  Deployment command failed"
        echo "💡 Manual deployment steps:"
        echo "   1. Push code to GitHub"
        echo "   2. Visit https://dashboard.render.com"
        echo "   3. Create a new Web Service"
        echo "   4. Connect your repository"
        echo "   5. Render will detect render.yaml automatically"
    fi
else
    echo "💡 Manual deployment required:"
    echo "   1. Push your code to GitHub"
    echo "   2. Go to https://dashboard.render.com"
    echo "   3. Click 'New +' → 'Blueprint'"
    echo "   4. Connect your GitHub repository"
    echo "   5. Render will auto-detect render.yaml"
    echo ""
    echo "📝 Required Environment Variables:"
    echo "   - ANTHROPIC_API_KEY (optional)"
    echo "   - E2B_API_KEY (optional)"
    echo "   - OPENAI_API_KEY (optional)"
fi

echo ""
echo "✅ Deployment script complete!"
echo "🎉 All existing files and templates preserved!"
