# Microsoft 365 Document Migration System

Complete document migration solution for Microsoft 365 (OneDrive and SharePoint) with support for multiple storage targets, batch processing, and automated scheduling.

## Features

### Core Features
- ✅ **OneDrive Migration** - Extract all files from OneDrive
- ✅ **SharePoint Migration** - Extract files from all accessible SharePoint sites
- ✅ **Batch Processing** - Handle large document libraries efficiently
- ✅ **Resumable Migrations** - Continue from where you left off
- ✅ **Concurrent Downloads** - Multi-threaded downloading for speed
- ✅ **Automatic Retry** - Retry failed downloads with exponential backoff

### Storage Targets
- ✅ **Local Storage** - Save to filesystem
- ✅ **Google Drive** - Upload directly to Google Drive
- ✅ **SharePoint** - Migrate to different SharePoint tenant
- ✅ **Multiple Targets** - Save to multiple destinations simultaneously

### Advanced Features
- ✅ **Scheduled Backups** - Automated daily/weekly migrations
- ✅ **Incremental Backups** - Only migrate new/changed files
- ✅ **File Filtering** - Filter by type, size, date, patterns
- ✅ **Progress Tracking** - Real-time progress bars and statistics
- ✅ **Metadata Preservation** - Save file dates, paths, and properties
- ✅ **Email Notifications** - Get notified on completion/failure
- ✅ **Verification Tools** - Verify migration completeness
- ✅ **Detailed Reports** - JSON, CSV, and HTML reports

## Architecture

```
microsoft365_migration.py       # Base migration engine
enhanced_migration.py           # Enhanced version with batch processing
migration_scheduler.py          # Automated scheduling system
test_authentication.py          # Authentication testing tool
verify_migration.py            # Migration verification tool

config.example.json            # Configuration template
requirements.txt               # Python dependencies
.env.example                   # Environment variables template

MIGRATION_SETUP_GUIDE.md       # Comprehensive setup guide
QUICKSTART.md                  # 15-minute quick start guide
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Register Azure AD App
- Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
- Create new registration
- Add API permissions: Files.Read.All, Sites.Read.All, User.Read
- Copy Client ID

### 3. Set Environment Variable
```bash
export MICROSOFT365_CLIENT_ID="your-client-id"
```

### 4. Test Authentication
```bash
python test_authentication.py
```

### 5. Run Migration
```bash
# Test with 5 files
python enhanced_migration.py --test

# Full migration
python enhanced_migration.py --full --batch
```

For detailed instructions, see **QUICKSTART.md**

## Documentation

| Document | Description |
|----------|-------------|
| **QUICKSTART.md** | Get started in 15 minutes |
| **MIGRATION_SETUP_GUIDE.md** | Complete setup and configuration guide |
| **config.example.json** | Configuration file reference |
| **.env.example** | Environment variables reference |

## Usage Examples

### Basic Migration
```bash
# Migrate everything
python enhanced_migration.py --full

# OneDrive only
python enhanced_migration.py --full --onedrive-only

# SharePoint only
python enhanced_migration.py --full --sharepoint-only
```

### Batch Processing
```bash
# Use batch mode with custom size
python enhanced_migration.py --batch --batch-size 100

# Resume failed migration
python enhanced_migration.py --resume
```

### Scheduled Backups
```bash
# Start scheduler (runs in background)
python migration_scheduler.py start --daemon

# Check status
python migration_scheduler.py status

# Stop scheduler
python migration_scheduler.py stop

# Run migration immediately
python migration_scheduler.py run-now
```

### Verification
```bash
# Verify migration completeness
python verify_migration.py

# Specify output directory
python verify_migration.py --output-dir /path/to/migrated-docs
```

## Configuration

### Basic Configuration (config.json)

```json
{
  "microsoft365": {
    "client_id": "your-client-id",
    "tenant_id": "common",
    "include_onedrive": true,
    "include_sharepoint": true
  },
  "migration_targets": {
    "local": {
      "enabled": true,
      "output_dir": "/home/user/migrated-docs"
    }
  },
  "batch_processing": {
    "enabled": true,
    "batch_size": 50,
    "concurrent_downloads": 5
  }
}
```

### Advanced Configuration

See `config.example.json` for all available options including:
- File filters (type, size, date, patterns)
- Multiple storage targets
- Email notifications
- Webhook integrations
- Scheduling settings
- Security options

## Migration Targets

### Local Storage
Save files to local filesystem with preserved folder structure.

```json
"local": {
  "enabled": true,
  "output_dir": "/home/user/migrated-docs",
  "preserve_structure": true
}
```

### Google Drive
Upload directly to Google Drive.

```json
"google_drive": {
  "enabled": true,
  "credentials_file": "google_credentials.json",
  "folder_name": "Microsoft 365 Migration"
}
```

Setup: See `MIGRATION_SETUP_GUIDE.md` Section "Google Drive Setup"

### SharePoint (Different Tenant)
Migrate to another SharePoint tenant.

```json
"sharepoint_target": {
  "enabled": true,
  "site_url": "https://yourtenant.sharepoint.com/sites/archive",
  "client_id": "...",
  "client_secret": "..."
}
```

## Scheduling

### Daily Backups
```json
{
  "scheduling": {
    "enabled": true,
    "schedule_type": "daily",
    "schedule_time": "02:00",
    "incremental_backup": true
  }
}
```

### Weekly Backups
```json
{
  "scheduling": {
    "enabled": true,
    "schedule_type": "weekly",
    "days_of_week": [1, 2, 3, 4, 5],
    "schedule_time": "02:00"
  }
}
```

Start scheduler:
```bash
python migration_scheduler.py start --daemon
```

## File Filtering

### Filter by File Type
```json
{
  "filters": {
    "file_types": [".pdf", ".docx", ".xlsx", ".pptx"]
  }
}
```

### Filter by Size
```json
{
  "filters": {
    "min_size_bytes": 1024,
    "max_size_bytes": 104857600
  }
}
```

### Exclude Patterns
```json
{
  "filters": {
    "exclude_patterns": ["*.tmp", "~*", "desktop.ini"]
  }
}
```

## Monitoring & Notifications

### Email Notifications
```json
{
  "notifications": {
    "enabled": true,
    "email": {
      "enabled": true,
      "recipient": "you@example.com",
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587
    }
  }
}
```

### Webhook Notifications
```json
{
  "notifications": {
    "webhook": {
      "enabled": true,
      "url": "https://your-webhook-url.com",
      "method": "POST"
    }
  }
}
```

## Logging

Logs are saved to:
```
/home/user/Private-Claude/logs/system-integration/
├── microsoft365_migration_YYYYMMDD_HHMMSS.log
├── scheduler.log
└── ...
```

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python enhanced_migration.py --full
```

## Reports

After migration, find reports in output directory:

```
/home/user/migrated-docs/
├── migration_report.json          # Detailed JSON report
├── migration_report.csv           # CSV format for Excel
├── enhanced_migration_report.json # Batch statistics
├── verification_report.json       # Verification results
└── migration_state.json          # Resume state
```

## Security

### Best Practices
1. **Protect credentials** - Use environment variables, not hardcoded values
2. **Secure storage** - Set proper file permissions (chmod 700)
3. **Encrypt output** - Enable encryption in config
4. **Clean up** - Remove temporary files and clear cache
5. **Audit trail** - Keep logs for compliance

### Encryption
```json
{
  "security": {
    "encrypt_output": true,
    "encryption_password": "your-strong-password",
    "clear_cache_on_exit": true
  }
}
```

## Performance

### Optimization Tips
1. **Adjust concurrent downloads** - Increase for faster speed (but watch bandwidth)
2. **Tune batch size** - Larger batches = fewer checkpoint saves
3. **Use filtering** - Skip unnecessary files
4. **Enable resumable downloads** - For large files
5. **Local network** - Run on server with good connection

### Typical Performance
| Document Count | Avg Speed | Est. Time |
|---------------|-----------|-----------|
| < 1,000 | ~50/min | 20 min |
| 1,000-10,000 | ~100/min | 1-2 hrs |
| 10,000-50,000 | ~150/min | 3-6 hrs |
| > 50,000 | ~200/min | 4-12 hrs |

*Speeds vary based on file sizes and network*

## Troubleshooting

### Authentication Issues
```bash
# Clear token cache
rm -rf ~/.msal_token_cache

# Test authentication
python test_authentication.py
```

### Permission Errors
- Verify API permissions in Azure AD
- Grant admin consent if required
- Check account has access to files

### Download Failures
- Increase timeout in config
- Reduce concurrent downloads
- Enable retry with exponential backoff

### Large Files
- Increase chunk size
- Enable resumable downloads
- Download separately if needed

See **MIGRATION_SETUP_GUIDE.md** for detailed troubleshooting.

## Development

### Project Structure
```
system-integration/
├── microsoft365_migration.py      # Core migration engine
├── enhanced_migration.py          # Enhanced features
├── migration_scheduler.py         # Scheduling system
├── test_authentication.py         # Auth testing
├── verify_migration.py           # Verification tool
├── config.example.json           # Config template
├── requirements.txt              # Dependencies
└── docs/
    ├── MIGRATION_SETUP_GUIDE.md  # Full guide
    ├── QUICKSTART.md             # Quick start
    └── README_MIGRATION.md       # This file
```

### Running Tests
```bash
# Test authentication
python test_authentication.py

# Test with small batch
python enhanced_migration.py --test --limit 5

# Verify migration
python verify_migration.py
```

## Support

### Resources
- **Setup Guide:** MIGRATION_SETUP_GUIDE.md
- **Quick Start:** QUICKSTART.md
- **Microsoft Graph API:** https://docs.microsoft.com/graph/
- **Google Drive API:** https://developers.google.com/drive/

### Common Questions

**Q: Will this delete my files?**
A: No, this tool only reads and downloads. Original files remain unchanged.

**Q: Can I resume if interrupted?**
A: Yes, use `--resume` flag to continue from last checkpoint.

**Q: Are versions preserved?**
A: Only current version is migrated. Version history is not preserved.

**Q: What about shared files?**
A: Any files you have read access to will be migrated.

**Q: Is data encrypted during transfer?**
A: Yes, all transfers use HTTPS/TLS encryption.

## License & Disclaimer

This tool is provided for research, development, and educational purposes.

- Use at your own risk
- Test thoroughly before production use
- Verify all data after migration
- Maintain backups of important data
- Comply with your organization's policies

## Version History

- **v2.0** - Enhanced migration with batch processing and multiple targets
- **v1.0** - Initial release with basic OneDrive and SharePoint support

## Contributing

This is a personal project for Private-Claude system integration.

---

**Quick Start:** See `QUICKSTART.md`
**Full Documentation:** See `MIGRATION_SETUP_GUIDE.md`

---

Last Updated: 2025-12-24
