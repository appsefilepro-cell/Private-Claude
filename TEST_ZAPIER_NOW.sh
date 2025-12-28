#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "           ZAPIER WEBHOOK TEST"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Enter your Zapier webhook URL:"
echo "(Get it from: https://zapier.com/app/zaps)"
echo ""
read -p "Webhook URL: " WEBHOOK_URL

if [ -z "$WEBHOOK_URL" ]; then
    echo "❌ No webhook URL provided"
    exit 1
fi

echo ""
echo "Testing webhook..."
echo ""

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "test",
    "source": "Agent X5",
    "message": "Zapier integration working!",
    "timestamp": "'"$(date -Iseconds)"'",
    "data": {
      "task": "Document draft request",
      "priority": "high"
    }
  }'

echo ""
echo ""
echo "✅ Test sent!"
echo "Check Zapier dashboard to see if it received the data"
echo ""
echo "Save this URL to config/.env:"
echo "ZAPIER_WEBHOOK_URL=$WEBHOOK_URL"
echo ""
