# Zapier Setup - 5 Minutes

## Step 1: Get Your Webhook URL (2 minutes)

1. Go to https://zapier.com/app/zaps
2. Click "Create Zap"
3. For trigger, search "Webhooks by Zapier"
4. Select "Catch Hook"
5. Click "Continue"
6. **COPY THE WEBHOOK URL** - looks like:
   ```
   https://hooks.zapier.com/hooks/catch/123456/abcdef
   ```

## Step 2: Test It (1 minute)

Open `scripts/zapier_webhook_sender.py` and:

1. Replace `YOUR_WEBHOOK_ID/YOUR_HOOK_ID` with your actual webhook URL
2. Run:
   ```bash
   python scripts/zapier_webhook_sender.py
   ```

You should see: `✅ Sent to Zapier successfully`

## Step 3: Set Up Action in Zapier (2 minutes)

Back in Zapier:

1. Click "Test trigger" - you should see your data
2. Click "Continue"
3. Choose action: **Gmail - Send Email** or **Google Sheets - Add Row**
4. Connect your account
5. Map the fields:
   - To: `appsefilepro@gmail.com`
   - Subject: `Task completed`
   - Body: Use the data fields Zapier shows you
6. Click "Test" then "Publish"

## Done!

Now every time you run the Python script, Zapier will send you an email or add to your sheet.

## Add to Your Code

```python
from scripts.zapier_webhook_sender import send_to_zapier

# When task completes
send_to_zapier(
    "https://hooks.zapier.com/hooks/catch/YOUR_URL_HERE",
    {"task": "Done", "status": "success"}
)
```

That's it. No complicated setup.
