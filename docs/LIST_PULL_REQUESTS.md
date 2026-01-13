# List Open Pull Requests

This directory contains utilities to list the latest open pull requests in the Private-Claude repository.

## Available Tools

### 1. list_prs.sh (Recommended)
A wrapper script that tries multiple methods to list PRs:

```bash
# List 10 latest open PRs (default)
./scripts/list_prs.sh

# List specific number of PRs
./scripts/list_prs.sh 5
```

**Methods tried (in order):**
1. GitHub CLI (`gh`) - Fastest and most reliable
2. Python script with GitHub API
3. Provides manual URL if tools unavailable

### 2. list_open_pull_requests.py
Direct Python script using GitHub API:

```bash
# Basic usage
python3 scripts/list_open_pull_requests.py

# List specific number
python3 scripts/list_open_pull_requests.py 5

# With authentication (recommended for better rate limits)
export GITHUB_TOKEN="your_token_here"
python3 scripts/list_open_pull_requests.py
```

## Setup Instructions

### Option A: GitHub CLI (Recommended)

1. Install GitHub CLI:
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

2. Authenticate:
   ```bash
   gh auth login
   ```

3. Run the script:
   ```bash
   ./scripts/list_prs.sh
   ```

### Option B: Python Script

1. Install Python 3 (if not already installed)

2. Install required dependencies:
   ```bash
   pip install requests
   ```

3. (Optional) Set up GitHub token for higher rate limits:
   ```bash
   export GITHUB_TOKEN="your_personal_access_token"
   ```

4. Run the script:
   ```bash
   python3 scripts/list_open_pull_requests.py
   ```

### Option C: Manual Check

Simply visit: https://github.com/appsefilepro-cell/Private-Claude/pulls

## Environment Variables

The scripts support the following environment variables:

- `GITHUB_TOKEN` - Personal access token for API authentication (optional but recommended)
- `GITHUB_OWNER` - Repository owner (default: "appsefilepro-cell")
- `GITHUB_REPO` - Repository name (default: "Private-Claude")

## Output Format

The scripts display:
- PR number and title
- Author
- Creation date
- Status (Draft or Ready for Review)
- URL
- Labels (if any)
- Assignees (if any)

## Example Output

```
====================================================================================================
  GitHub Pull Requests Viewer - appsefilepro-cell/Private-Claude
====================================================================================================

📋 Latest Open Pull Requests (10 total)

====================================================================================================

1. PR #186: [WIP] List latest open pull requests
   Author: Copilot
   Created: 2026-01-13 00:16:20 UTC
   Status: 🟢 Draft
   URL: https://github.com/appsefilepro-cell/Private-Claude/pull/186

----------------------------------------------------------------------------------------------------

2. PR #185: Document task analysis and clarify system state
   Author: Copilot
   Created: 2026-01-13 00:08:22 UTC
   Status: 🟢 Draft
   URL: https://github.com/appsefilepro-cell/Private-Claude/pull/185
   Labels: good first issue, EXECUTE ALL CLAUDE CODE COMMANDS AND GITHUB AI

----------------------------------------------------------------------------------------------------
...
```

## Troubleshooting

### "Error fetching pull requests: 403 Client Error"
- You've hit the GitHub API rate limit
- Solution: Set `GITHUB_TOKEN` environment variable with a personal access token
- Or: Use GitHub CLI which handles authentication better

### "gh: To use GitHub CLI... set the GH_TOKEN environment variable"
- Running in GitHub Actions or similar CI environment
- Solution: Set `GH_TOKEN` environment variable:
  ```bash
  export GH_TOKEN="${{ github.token }}"  # In GitHub Actions
  ```

### "Neither GitHub CLI (gh) nor Python 3 found"
- Install either GitHub CLI or Python 3 (see Setup Instructions above)
- Or visit the repository directly in your browser

## Integration with Agent X5

These scripts can be integrated into the Agent X5 orchestration system for automated PR monitoring and reporting.

Example integration:
```python
import subprocess
import json

# Get PRs as structured data
result = subprocess.run(
    ["gh", "pr", "list", "--json", "number,title,author,createdAt"],
    capture_output=True,
    text=True
)
prs = json.loads(result.stdout)

# Process PRs with Agent X5
for pr in prs:
    print(f"Processing PR #{pr['number']}: {pr['title']}")
```

## Additional Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub API Documentation](https://docs.github.com/en/rest/pulls/pulls)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

---

**Agent X5.0** - *219 Agents Working in Parallel*

*Version 5.0.0 | January 2026 | APPS Holdings WY Inc.*
