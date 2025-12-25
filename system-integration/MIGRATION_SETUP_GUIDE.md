# Microsoft 365 Document Migration - Complete Setup Guide

## Overview
This guide will help you migrate all your documents from Microsoft 365 (OneDrive and SharePoint) to alternative storage solutions before your subscription ends.

**Supported Migration Targets:**
- Local storage (filesystem)
- Google Drive
- SharePoint (other tenants)
- Any combination of the above

---

## Prerequisites

- Python 3.8 or higher
- Active Microsoft 365 account with documents to migrate
- Internet connection
- Administrator access to Azure AD (for app registration)

---

## Part 1: Azure AD Application Setup

### Step 1: Register Azure AD Application

1. **Navigate to Azure Portal:**
   - Go to: https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
   - Sign in with your Microsoft 365 account

2. **Create New Registration:**
   - Click **"New registration"**
   - Application name: `Document Migration Tool`
   - Supported account types:
     - For personal Microsoft accounts: Select **"Personal Microsoft accounts only"**
     - For work/school accounts: Select **"Accounts in this organizational directory only"**
   - Redirect URI: Leave blank (we use device code flow)
   - Click **"Register"**

3. **Copy Application (client) ID:**
   - On the Overview page, copy the **Application (client) ID**
   - Save this for later use

4. **Copy Directory (tenant) ID:**
   - Also on the Overview page, copy the **Directory (tenant) ID**
   - For personal accounts, you can use "common" instead

### Step 2: Configure API Permissions

1. **Navigate to API Permissions:**
   - In your app registration, click **"API permissions"** in the left menu

2. **Add Microsoft Graph Permissions:**
   - Click **"Add a permission"**
   - Select **"Microsoft Graph"**
   - Select **"Delegated permissions"**
   - Add the following permissions:
     - `Files.Read.All` - Read all files user can access
     - `Sites.Read.All` - Read items in all site collections
     - `User.Read` - Sign in and read user profile

3. **Grant Admin Consent (Optional):**
   - If using work/school account, click **"Grant admin consent"**
   - This step may be required by your organization

### Step 3: Enable Public Client Flow

1. **Navigate to Authentication:**
   - Click **"Authentication"** in the left menu

2. **Configure Platform:**
   - Under "Advanced settings" > "Allow public client flows"
   - Set to **"Yes"**
   - Click **"Save"**

---

## Part 2: Google Drive Setup (Optional)

If you want to migrate to Google Drive, follow these steps:

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Navigate to: https://console.cloud.google.com/

2. **Create New Project:**
   - Click "Select a project" > "New Project"
   - Project name: `Document Migration`
   - Click **"Create"**

3. **Enable Google Drive API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click **"Enable"**

### Step 2: Create OAuth Credentials

1. **Configure OAuth Consent Screen:**
   - Go to "APIs & Services" > "OAuth consent screen"
   - User type: **External**
   - App name: `Document Migration Tool`
   - Add your email as developer contact
   - Click **"Save and Continue"**

2. **Add Scopes:**
   - Click "Add or Remove Scopes"
   - Add: `https://www.googleapis.com/auth/drive.file`
   - Click **"Save and Continue"**

3. **Create OAuth Client ID:**
   - Go to "APIs & Services" > "Credentials"
   - Click **"Create Credentials"** > "OAuth client ID"
   - Application type: **Desktop app**
   - Name: `Migration Tool`
   - Click **"Create"**
   - Download the JSON credentials file
   - Save as `google_credentials.json` in the `system-integration` directory

---

## Part 3: Installation

### Step 1: Install Python Dependencies

```bash
cd /home/user/Private-Claude/system-integration

# Install required packages
pip install -r requirements.txt
```

### Step 2: Create Configuration File

Copy the example configuration:

```bash
cp config.example.json config.json
```

Edit `config.json` with your settings:

```json
{
  "microsoft365": {
    "client_id": "YOUR_AZURE_CLIENT_ID",
    "tenant_id": "common",
    "include_onedrive": true,
    "include_sharepoint": true
  },
  "migration_targets": {
    "local": {
      "enabled": true,
      "output_dir": "/home/user/migrated-docs"
    },
    "google_drive": {
      "enabled": false,
      "credentials_file": "google_credentials.json",
      "folder_name": "Microsoft 365 Migration"
    }
  },
  "batch_processing": {
    "enabled": true,
    "batch_size": 50,
    "concurrent_downloads": 5,
    "retry_failed": true,
    "max_retries": 3
  },
  "filters": {
    "file_types": [],
    "exclude_patterns": ["*.tmp", "~*"],
    "min_size_bytes": 0,
    "max_size_bytes": 5368709120
  },
  "scheduling": {
    "enabled": false,
    "schedule_type": "daily",
    "schedule_time": "02:00",
    "days_of_week": [1, 2, 3, 4, 5]
  }
}
```

### Step 3: Set Environment Variables

Create a `.env` file:

```bash
# Microsoft 365
MICROSOFT365_CLIENT_ID=your-client-id-here
MICROSOFT365_TENANT_ID=common

# Google Drive (optional)
GOOGLE_APPLICATION_CREDENTIALS=google_credentials.json
```

Or export directly:

```bash
export MICROSOFT365_CLIENT_ID="your-client-id-here"
export MICROSOFT365_TENANT_ID="common"
```

---

## Part 4: Testing the Setup

### Step 1: Test Microsoft 365 Authentication

Run the authentication test:

```bash
python test_authentication.py
```

This will:
1. Test connection to Microsoft Graph API
2. Verify your permissions
3. List accessible OneDrive and SharePoint sites
4. Display file counts and sizes

Expected output:
```
✅ Authentication successful
✅ OneDrive accessible
✅ SharePoint accessible
📊 Found X files in OneDrive (Y MB)
📊 Found Z SharePoint sites
```

### Step 2: Test with Small Batch

Perform a test migration with a small batch:

```bash
python microsoft365_migration.py --test --limit 5
```

This will migrate only 5 files to verify everything works.

---

## Part 5: Running the Migration

### Option 1: Full Migration (One-Time)

Migrate all documents at once:

```bash
python microsoft365_migration.py --full
```

Options:
- `--config config.json` - Use custom configuration
- `--onedrive-only` - Migrate only OneDrive files
- `--sharepoint-only` - Migrate only SharePoint files
- `--dry-run` - Show what would be migrated without downloading

### Option 2: Batch Migration

For large document libraries, use batch mode:

```bash
python microsoft365_migration.py --batch --batch-size 100
```

This processes documents in batches of 100, allowing you to:
- Pause and resume migration
- Handle network interruptions
- Track progress more granularly

### Option 3: Scheduled Backups

Set up automated daily backups:

1. **Configure scheduling in config.json:**
   ```json
   "scheduling": {
     "enabled": true,
     "schedule_type": "daily",
     "schedule_time": "02:00"
   }
   ```

2. **Start the scheduler:**
   ```bash
   python migration_scheduler.py start
   ```

3. **Check scheduler status:**
   ```bash
   python migration_scheduler.py status
   ```

4. **Stop the scheduler:**
   ```bash
   python migration_scheduler.py stop
   ```

### Option 4: Resume Failed Migration

If a migration fails or is interrupted:

```bash
python microsoft365_migration.py --resume
```

This will:
- Read the last migration report
- Skip already downloaded files
- Retry failed downloads
- Continue where it left off

---

## Part 6: Migration to Multiple Targets

### Migrate to Local + Google Drive

1. **Enable both targets in config.json:**
   ```json
   "migration_targets": {
     "local": {
       "enabled": true,
       "output_dir": "/home/user/migrated-docs"
     },
     "google_drive": {
       "enabled": true,
       "credentials_file": "google_credentials.json",
       "folder_name": "Microsoft 365 Migration"
     }
   }
   ```

2. **Run migration:**
   ```bash
   python microsoft365_migration.py --full
   ```

Files will be saved to both local storage AND uploaded to Google Drive.

### Migrate to Different SharePoint Tenant

1. **Configure target SharePoint in config.json:**
   ```json
   "migration_targets": {
     "sharepoint_target": {
       "enabled": true,
       "site_url": "https://yourtenant.sharepoint.com/sites/archive",
       "client_id": "target-sharepoint-client-id",
       "client_secret": "target-sharepoint-secret",
       "library_name": "Documents"
     }
   }
   ```

2. **Run migration:**
   ```bash
   python microsoft365_migration.py --full --target sharepoint
   ```

---

## Part 7: Monitoring and Verification

### View Migration Progress

During migration, monitor:

1. **Console output** - Real-time progress
2. **Log files** - `/home/user/Private-Claude/logs/system-integration/microsoft365_migration_*.log`
3. **Migration reports** - Generated in output directory

### Verify Migration Completeness

After migration completes:

1. **Check migration report:**
   ```bash
   cat /home/user/migrated-docs/migration_report.json
   ```

2. **Review statistics:**
   - Total files found
   - Successfully migrated
   - Failed downloads
   - Total size migrated

3. **Compare file counts:**
   ```bash
   python verify_migration.py
   ```

This compares source (Microsoft 365) vs destination file counts and sizes.

### Handle Failed Files

If some files failed to migrate:

1. **Review failed files:**
   ```bash
   cat /home/user/migrated-docs/failed_files.json
   ```

2. **Retry failed files:**
   ```bash
   python microsoft365_migration.py --retry-failed
   ```

---

## Part 8: Post-Migration Tasks

### Backup Migration Data

After successful migration:

1. **Create backup archive:**
   ```bash
   cd /home/user
   tar -czf microsoft365-migration-$(date +%Y%m%d).tar.gz migrated-docs/
   ```

2. **Copy to external storage** or cloud backup service

### Clean Up (Optional)

If migration is complete and verified:

1. **Remove metadata files:**
   ```bash
   find /home/user/migrated-docs -name "*.metadata.json" -delete
   ```

2. **Keep migration reports** for reference

### Cancel Microsoft 365 Subscription

Only after verifying all documents are safely migrated:

1. Confirm all files are accessible
2. Test opening various file types
3. Verify no corruption occurred
4. Cancel subscription through Microsoft admin portal

---

## Troubleshooting

### Authentication Issues

**Problem:** "Authentication failed" error

**Solutions:**
1. Verify client ID is correct
2. Check API permissions are granted
3. Enable public client flow in Azure AD
4. Clear token cache: `rm -rf ~/.msal_token_cache`

### Permission Errors

**Problem:** "Access denied" or "Forbidden" errors

**Solutions:**
1. Grant admin consent for API permissions
2. Verify your account has access to files
3. Check SharePoint site permissions
4. Re-authenticate: `python microsoft365_migration.py --reauth`

### Download Failures

**Problem:** Files failing to download

**Solutions:**
1. Check internet connection
2. Increase timeout in config: `"request_timeout": 300`
3. Reduce concurrent downloads: `"concurrent_downloads": 2`
4. Enable retry: `"retry_failed": true`

### Large File Issues

**Problem:** Very large files timing out

**Solutions:**
1. Increase chunk size: `"chunk_size_mb": 10`
2. Use resumable downloads: `"resumable_downloads": true`
3. Download large files separately with `--file-id` option

### Google Drive Upload Failures

**Problem:** "Quota exceeded" or upload errors

**Solutions:**
1. Check Google Drive storage quota
2. Verify credentials file is valid
3. Re-authenticate with Google: `python google_auth_test.py`
4. Enable resumable uploads in config

### Rate Limiting

**Problem:** "Too many requests" errors

**Solutions:**
1. Increase delay between requests: `"rate_limit_delay": 1.0`
2. Reduce concurrent downloads
3. Use batch mode with smaller batches
4. Enable exponential backoff: `"exponential_backoff": true`

---

## Advanced Configuration

### Custom File Filters

Only migrate specific file types:

```json
"filters": {
  "file_types": [".pdf", ".docx", ".xlsx", ".pptx"],
  "exclude_patterns": ["*.tmp", "~*", "desktop.ini"],
  "min_size_bytes": 1024,
  "max_size_bytes": 104857600
}
```

### Folder Structure Preservation

Maintain original folder structure:

```json
"preserve_structure": true,
"folder_mapping": {
  "/Documents": "/migrated-docs/documents",
  "/Pictures": "/migrated-docs/images"
}
```

### Email Notifications

Get notified when migration completes:

```json
"notifications": {
  "enabled": true,
  "email": "your-email@example.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "notifications@example.com",
  "smtp_password": "your-app-password"
}
```

---

## Security Best Practices

1. **Protect Credentials:**
   - Never commit credentials to git
   - Use environment variables or secure vaults
   - Rotate credentials after migration

2. **Secure Storage:**
   - Encrypt migrated files: `"encrypt_output": true`
   - Use secure file permissions: `chmod 700`
   - Store backups on encrypted drives

3. **Clean Up:**
   - Clear token cache after migration
   - Remove temporary files
   - Delete Azure AD app after use

4. **Audit Trail:**
   - Keep migration logs for compliance
   - Document all transferred files
   - Maintain metadata for forensics

---

## Support and Resources

### Documentation
- Microsoft Graph API: https://docs.microsoft.com/graph/
- Google Drive API: https://developers.google.com/drive/
- MSAL Python: https://github.com/AzureAD/microsoft-authentication-library-for-python

### Logging
- All operations are logged to: `/home/user/Private-Claude/logs/system-integration/`
- Enable debug logging: `--debug` flag

### Getting Help
- Check error logs first
- Review migration reports
- Test authentication separately
- Use `--dry-run` to verify configuration

---

## Quick Reference Commands

```bash
# Test authentication
python test_authentication.py

# Full migration
python microsoft365_migration.py --full

# Batch migration
python microsoft365_migration.py --batch --batch-size 100

# Resume failed
python microsoft365_migration.py --resume

# Dry run
python microsoft365_migration.py --dry-run

# Start scheduler
python migration_scheduler.py start

# Check status
python migration_scheduler.py status

# Verify migration
python verify_migration.py
```

---

## Estimated Migration Times

| Document Count | Total Size | Estimated Time |
|---------------|------------|----------------|
| < 1,000       | < 1 GB     | 15-30 minutes  |
| 1,000-10,000  | 1-10 GB    | 1-3 hours      |
| 10,000-50,000 | 10-50 GB   | 3-8 hours      |
| > 50,000      | > 50 GB    | 8-24+ hours    |

*Times vary based on internet speed and file sizes*

---

## FAQ

**Q: Will this delete files from Microsoft 365?**
A: No, this tool only reads and downloads files. Original files remain unchanged.

**Q: Can I resume if migration is interrupted?**
A: Yes, use `--resume` flag to continue from where it stopped.

**Q: What happens to file versions?**
A: Only the current version is migrated. Version history is not preserved.

**Q: Are permissions preserved?**
A: No, only file content and basic metadata (dates, names) are preserved.

**Q: Can I migrate shared files?**
A: Yes, any files you have read access to will be migrated.

**Q: What about very large files (>100GB)?**
A: Large files use chunked downloads. Adjust `chunk_size_mb` in config as needed.

**Q: Is my data encrypted during transfer?**
A: Yes, all transfers use HTTPS/TLS encryption.

---

## License and Disclaimer

This tool is provided for research, development, and educational purposes.

- Use at your own risk
- Test thoroughly before full migration
- Verify all data after migration
- Maintain backups of important data
- Comply with your organization's data policies

---

**Last Updated:** 2025-12-24
**Version:** 2.0
