# 🚨 URGENT: EXTRACT YOUR MICROSOFT 365 DOCUMENTS NOW

## Your subscription is ending - get your documents out IMMEDIATELY!

---

## ⚡ FASTEST WAY - Run ONE Command:

```bash
cd /home/user/Private-Claude
./EXTRACT_DOCUMENTS_NOW.sh
```

**That's it!** The script will guide you through everything.

---

## 📋 What Happens:

1. **Installs dependencies** (automatic - takes 30 seconds)
2. **Checks authentication** (one-time setup - takes 2 minutes)
3. **Scans your Microsoft 365** (finds all files)
4. **Downloads EVERYTHING** (OneDrive + SharePoint)
5. **Saves locally** to `/home/user/Private-Claude/migrated-docs/`
6. **Creates reports** (JSON and CSV)

---

## 🔑 First-Time Setup (2 Minutes):

If this is your first time, you need to create an Azure AD app (free, no credit card):

### Quick Steps:

1. **Go to Azure Portal:**
   ```
   https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
   ```

2. **Click "New registration"**

3. **Fill the form:**
   - **Name:** `Document Migration Tool`
   - **Account types:** Select **third option** (Any organizational directory + Personal)
   - **Redirect URI:** Leave BLANK
   - Click **Register**

4. **Copy the Application (client) ID**
   - It looks like: `12345678-abcd-1234-abcd-123456789abc`

5. **Add Permissions:**
   - Left menu → "API permissions"
   - Click "+ Add a permission"
   - Choose "Microsoft Graph"
   - Choose "Delegated permissions"
   - Search and check:
     - ✅ `Files.Read.All`
     - ✅ `Sites.Read.All`
     - ✅ `User.Read`
   - Click "Add permissions"

6. **Set the Client ID in your terminal:**
   ```bash
   export MICROSOFT365_CLIENT_ID='paste-your-client-id-here'
   ```

7. **Run the extraction script:**
   ```bash
   ./EXTRACT_DOCUMENTS_NOW.sh
   ```

---

## 🔐 Authentication During Extraction:

When you run the script, you'll see:

```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code: ABC12DEF3
```

**What to do:**
1. Open https://microsoft.com/devicelogin in your browser
2. Enter the code shown (e.g., `ABC12DEF3`)
3. Sign in with your Microsoft 365 account
4. Click "Accept" to grant permissions
5. Return to terminal - download starts automatically!

---

## 📁 Where Are My Documents?

After extraction completes:

```
/home/user/Private-Claude/migrated-docs/
├── onedrive/              ← All your OneDrive files
├── sharepoint/            ← All your SharePoint files
├── migration_report.json  ← Detailed report
└── migration_report.csv   ← Easy-to-read spreadsheet
```

---

## ⏱️ How Long Does This Take?

- **Setup:** 2 minutes (one-time only)
- **Scanning:** 30 seconds - 2 minutes
- **Download:** Depends on file size
  - 100 files (~500MB): ~5 minutes
  - 1000 files (~5GB): ~30 minutes
  - 10000 files (~50GB): ~3 hours

---

## ❓ Troubleshooting:

### "Authentication failed"
- Make sure you added all 3 permissions in Azure Portal
- Try running the script again (sometimes it takes a minute for permissions to activate)

### "No module named 'msal'"
- The script installs it automatically, but if it fails:
  ```bash
  pip3 install msal requests
  ```

### "Client ID not configured"
- Make sure you ran the export command:
  ```bash
  export MICROSOFT365_CLIENT_ID='your-client-id-here'
  ```
- Note: This only lasts for your current terminal session

### Want to save the Client ID permanently?
```bash
echo "export MICROSOFT365_CLIENT_ID='your-client-id-here'" >> ~/.bashrc
source ~/.bashrc
```

---

## 🎯 Quick Command Reference:

```bash
# Run the extraction
cd /home/user/Private-Claude
./EXTRACT_DOCUMENTS_NOW.sh

# Set Client ID (replace with yours)
export MICROSOFT365_CLIENT_ID='12345678-abcd-1234-abcd-123456789abc'

# Check what was downloaded
ls -lh /home/user/Private-Claude/migrated-docs/

# View the report
cat /home/user/Private-Claude/migrated-docs/migration_report.csv
```

---

## ✅ After Extraction:

1. **Verify your documents** are in `/home/user/Private-Claude/migrated-docs/`
2. **Check the reports** to ensure everything was downloaded
3. **Backup the migrated-docs folder** to external storage or cloud
4. **Cancel your Microsoft 365 subscription** (your documents are safe!)

---

## 🆘 Need Help?

1. **Detailed guide:** `/home/user/Private-Claude/system-integration/MIGRATION_SETUP_GUIDE.md`
2. **Check logs:** `/home/user/Private-Claude/logs/system-integration/`

---

## 🚀 START NOW:

```bash
cd /home/user/Private-Claude
./EXTRACT_DOCUMENTS_NOW.sh
```

**Don't wait - your subscription is ending!**
