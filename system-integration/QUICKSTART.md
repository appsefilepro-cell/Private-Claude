# Microsoft 365 Migration - Quick Start Guide

This guide will get you up and running with Microsoft 365 document migration in 15 minutes.

## Prerequisites

- Python 3.8+
- Microsoft 365 account with documents
- 15 minutes of your time

---

## Step 1: Install Dependencies (2 minutes)

```bash
cd /home/user/Private-Claude/system-integration

# Install Python packages
pip install -r requirements.txt
```

---

## Step 2: Register Azure AD Application (5 minutes)

1. **Go to Azure Portal:**
   - Visit: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
   - Sign in with your Microsoft 365 account

2. **Create New Registration:**
   - Click "New registration"
   - Name: `Document Migration Tool`
   - Account types: Select "Personal Microsoft accounts only" (or your org type)
   - Redirect URI: Leave blank
   - Click "Register"

3. **Copy Client ID:**
   - On the Overview page, copy the "Application (client) ID"
   - Keep this for the next step

4. **Add API Permissions:**
   - Click "API permissions" → "Add a permission"
   - Select "Microsoft Graph" → "Delegated permissions"
   - Add these permissions:
     - Files.Read.All
     - Sites.Read.All
     - User.Read
   - Click "Add permissions"

5. **Enable Public Client:**
   - Click "Authentication"
   - Under "Advanced settings" → "Allow public client flows" → Set to "Yes"
   - Click "Save"

---

## Step 3: Configure Environment (2 minutes)

```bash
# Set your client ID (replace with your actual ID)
export MICROSOFT365_CLIENT_ID="your-client-id-here"

# For personal accounts, use 'common'
export MICROSOFT365_TENANT_ID="common"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your client ID
```

---

## Step 4: Test Authentication (3 minutes)

```bash
python test_authentication.py
```

This will:
- Prompt you to authenticate via web browser
- Test all permissions
- Show file counts and storage usage
- Verify everything is working

Expected output:
```
✅ Authentication successful
✅ OneDrive accessible
✅ SharePoint accessible
📊 Found X files
```

---

## Step 5: Run Migration (3 minutes for test, longer for full)

### Option A: Test Migration (first 5 files)

```bash
python enhanced_migration.py --test
```

This migrates just 5 files to verify everything works.

### Option B: Full Migration

```bash
python enhanced_migration.py --full --batch
```

This migrates all your documents with batch processing.

---

## Default Settings

Unless you change the configuration, migration will:

- ✅ Download all OneDrive files
- ✅ Download all SharePoint files
- ✅ Save to `/home/user/migrated-docs`
- ✅ Preserve folder structure
- ✅ Create metadata files
- ✅ Process in batches of 50 files
- ✅ Use 5 concurrent downloads
- ✅ Auto-retry failed downloads

---

## Where Are My Files?

After migration completes:

```bash
# View migrated files
ls -lah /home/user/migrated-docs/

# View migration report
cat /home/user/migrated-docs/migration_report.json

# Verify migration completeness
python verify_migration.py
```

---

## Common Issues

### "Client ID not configured"
```bash
export MICROSOFT365_CLIENT_ID="your-actual-client-id"
```

### "Permission denied"
Make sure you added all three API permissions in Step 2.

### "Authentication failed"
- Clear cache: `rm -rf ~/.msal_token_cache`
- Try again: `python test_authentication.py`

---

## Next Steps

### Customize Configuration

```bash
# Copy example config
cp config.example.json config.json

# Edit config.json to customize:
# - Batch size
# - Output directory
# - File filters
# - Additional targets (Google Drive)
```

### Schedule Automated Backups

```bash
# Edit config.json, set scheduling.enabled = true
# Then start scheduler:
python migration_scheduler.py start
```

### Migrate to Multiple Targets

```bash
# Edit config.json to enable Google Drive or other targets
# Then run:
python enhanced_migration.py --full
```

---

## Getting Help

1. **Read the full guide:** `MIGRATION_SETUP_GUIDE.md`
2. **Check logs:** `/home/user/Private-Claude/logs/system-integration/`
3. **Test authentication:** `python test_authentication.py`
4. **Verify migration:** `python verify_migration.py`

---

## Quick Command Reference

```bash
# Test authentication
python test_authentication.py

# Test migration (5 files)
python enhanced_migration.py --test

# Full migration
python enhanced_migration.py --full --batch

# Resume failed migration
python enhanced_migration.py --resume

# Verify migration
python verify_migration.py

# Start scheduler
python migration_scheduler.py start

# Check scheduler status
python migration_scheduler.py status
```

---

**That's it! You're ready to migrate your Microsoft 365 documents.**

For advanced features and troubleshooting, see `MIGRATION_SETUP_GUIDE.md`
