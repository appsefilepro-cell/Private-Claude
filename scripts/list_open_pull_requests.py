#!/usr/bin/env python3
"""
Script to list the latest open pull requests in the Private-Claude repository.

This script uses the GitHub API to fetch and display open pull requests,
showing key information like PR number, title, author, and creation date.
"""

import os
import sys
import json
from datetime import datetime
try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Please install it with: pip install requests")
    sys.exit(1)


def list_open_pull_requests(owner="appsefilepro-cell", repo="Private-Claude", token=None, limit=10):
    """
    List the latest open pull requests for a GitHub repository.
    
    Args:
        owner: Repository owner (default: "appsefilepro-cell")
        repo: Repository name (default: "Private-Claude")
        token: GitHub personal access token (optional, for higher rate limits)
        limit: Maximum number of PRs to display (default: 10)
    
    Returns:
        List of pull request dictionaries
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    params = {
        "state": "open",
        "sort": "created",
        "direction": "desc",
        "per_page": limit
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching pull requests: {e}")
        return []


def format_date(date_string):
    """Format ISO 8601 date string to readable format."""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return date_string


def display_pull_requests(pull_requests):
    """Display pull requests in a readable format."""
    if not pull_requests:
        print("\n✅ No open pull requests found.")
        return
    
    print(f"\n📋 Latest Open Pull Requests ({len(pull_requests)} total)\n")
    print("=" * 100)
    
    for i, pr in enumerate(pull_requests, 1):
        print(f"\n{i}. PR #{pr['number']}: {pr['title']}")
        print(f"   Author: {pr['user']['login']}")
        print(f"   Created: {format_date(pr['created_at'])}")
        print(f"   Status: {'🟢 Draft' if pr.get('draft', False) else '✅ Ready for Review'}")
        print(f"   URL: {pr['html_url']}")
        
        # Show labels if any
        if pr.get('labels'):
            labels = [label['name'] for label in pr['labels']]
            print(f"   Labels: {', '.join(labels)}")
        
        # Show assignees if any
        if pr.get('assignees'):
            assignees = [assignee['login'] for assignee in pr['assignees']]
            print(f"   Assignees: {', '.join(assignees)}")
        
        print("-" * 100)


def main():
    """Main function to run the script."""
    print("=" * 100)
    print("  GitHub Pull Requests Viewer - Private-Claude Repository")
    print("=" * 100)
    
    # Get GitHub token from environment variable (optional)
    github_token = os.getenv("GITHUB_TOKEN")
    
    # Get repository info from environment or use defaults
    owner = os.getenv("GITHUB_OWNER", "appsefilepro-cell")
    repo = os.getenv("GITHUB_REPO", "Private-Claude")
    
    # Get limit from command line argument or use default
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid limit '{sys.argv[1]}', using default of 10")
    
    if github_token:
        print("✓ Using GitHub authentication token")
    else:
        print("ℹ No GitHub token found. Using unauthenticated API (lower rate limit)")
        print("  Set GITHUB_TOKEN environment variable for higher rate limits.")
    
    print(f"\nFetching open pull requests from {owner}/{repo}...")
    
    # Fetch and display pull requests
    pull_requests = list_open_pull_requests(owner, repo, github_token, limit)
    display_pull_requests(pull_requests)
    
    print("\n" + "=" * 100)
    print(f"✅ Done! Showing {len(pull_requests)} open pull request(s).")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
