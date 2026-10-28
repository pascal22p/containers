#!/usr/bin/env python3
"""
Create Jira tickets from Renovate PR creation log entries.
Uses a local state file to avoid creating duplicate tickets for already processed PRs.
Validates that each PR exists and is still open.
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
import requests
from requests.exceptions import RequestException

# ======================
# Configuration
# ======================
JIRA_URL = os.getenv("JIRA_URL", "https://your-domain.atlassian.net")
JIRA_BEARER_TOKEN = os.getenv("JIRA_BEARER_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # needed for private repos

PROJECT_KEY = os.getenv("PROJECT_KEY", "PROJ")
ISSUE_TYPE = os.getenv("ISSUE_TYPE", "Task")

LOG_FILE = os.getenv("RENOVATE_LOG_FILE", "renovate/renovate.log")
HOURS_LOOKBACK = int(os.getenv("HOURS_LOOKBACK", "6"))
STATE_FILE = os.getenv("STATE_FILE", "last_jira_pr.json")


def load_state(state_file: str) -> dict:
    if not os.path.exists(state_file):
        return {}
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # If the old state file was a single flat dict (old format), handle migration/fallback
            if isinstance(data, dict) and "repository" in data and "pr" in data:
                old_key = f"{data['repository']}#{data['pr']}"
                return {old_key: data}
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state_file: str, data: dict):
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_all_prs_created(log_file: str, hours: int = 6) -> list:
    """Parse renovate.log and return a list of all 'PR created' entries within the lookback window."""
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        sys.exit(1)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    entries = []

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("msg") != "PR created":
                continue

            time_str = entry.get("time")
            if not time_str:
                continue

            try:
                entry_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            except ValueError:
                continue

            if entry_time < cutoff:
                continue

            entry["_parsed_time"] = entry_time
            entries.append(entry)

    # Sort chronologically (oldest to newest)
    entries.sort(key=lambda x: x["_parsed_time"])
    return entries


def build_pr_url(entry: dict) -> str | None:
    repository = entry.get("repository")
    pr_number = entry.get("pr")
    if not repository or not pr_number:
        return None
    return f"https://github.com/{repository}/pull/{pr_number}"


def validate_pr(repository: str, pr_number: int) -> dict | None:
    """
    Check that the PR exists and is open (not closed or merged).
    Returns the PR data if valid, otherwise None.
    """
    url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"

    headers = {
        "Accept": "application/vnd.github+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    print(f"→ Validating PR: {url}")
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        print(f"❌ PR #{pr_number} does not exist in {repository}")
        return None

    if response.status_code != 200:
        print(f"❌ Failed to fetch PR (HTTP {response.status_code})")
        print(response.text)
        return None

    pr = response.json()

    state = pr.get("state")          # "open" or "closed"
    merged = pr.get("merged", False)

    if state != "open":
        print(f"❌ PR #{pr_number} is not open (state={state}, merged={merged})")
        return None

    if merged:
        print(f"❌ PR #{pr_number} is already merged")
        return None

    print(f"✅ PR #{pr_number} exists and is open")
    return pr


def create_jira_ticket(summary: str, description: str) -> dict | None:
    if not JIRA_BEARER_TOKEN:
        print("Error: JIRA_BEARER_TOKEN environment variable is required")
        sys.exit(1)

    url = "xxxxx" #f"{JIRA_URL.rstrip('/')}/rest/api/2/issue"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JIRA_BEARER_TOKEN}"
    }

    payload = {
        "fields": {
            "project": {
                "key": PROJECT_KEY
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": ISSUE_TYPE
            }
        }
    }

    print(f"→ POST {url}")
    try:
        response = requests.post(url, json=payload, headers=headers)
    except RequestException as e:
        print(f"💥 Error while creating jira ticket with error {e}")
        return None

    print(f"← Status: {response.status_code}")
    print(f"← Response:\n{response.text}\n")

    if response.status_code in (200, 201):
        data = response.json()
        print(f"✅ Ticket created successfully!")
        print(f"    Key : {data.get('key')}")
        print(f"    URL : {JIRA_URL.rstrip('/')}/browse/{data.get('key')}")
        return data
    else:
        print(f"❌ Failed to create ticket (HTTP {response.status_code})")
        return None


def main():
    print(f"Looking for 'PR created' entries in the last {HOURS_LOOKBACK} hours...")
    entries = find_all_prs_created(LOG_FILE, HOURS_LOOKBACK)

    if not entries:
        print("No 'PR created' log entries found in the lookback window.")
        sys.exit(0)

    print(f"Found {len(entries)} 'PR created' entry/entries to process.")

    state = load_state(STATE_FILE)
    state_updated = False

    for entry in entries:
        repository = entry.get("repository")
        pr_number = entry.get("pr")
        pr_title = entry.get("prTitle", "Renovate PR")
        pr_url = build_pr_url(entry)
        branch = entry.get("branch", "unknown")
        created_at = entry.get("time")

        pr_key = f"{repository}#{pr_number}"

        print(f"\n--- Processing PR: {pr_title} (#{pr_number} in {repository}) ---")

        # ----- Duplicate check -----
        if pr_key in state:
            print(f"⏭️ Skipping – Jira ticket already created for this PR "
                  f"({state[pr_key].get('jiraKey', 'unknown')})")
            continue

        # ----- Validate PR exists and is open -----
        pr_data = validate_pr(repository, pr_number)
        if not pr_data:
            print("Skipping Jira ticket creation because PR is invalid or not open.")
            continue

        # Build Jira content
        summary = pr_title

        description = f"""Renovate created a new Pull Request.

*Repository:* {repository}
*Branch:* {branch}
*PR Number:* {pr_number}
*PR Title:* {pr_title}
*Created at:* {created_at}

PR URL: {pr_url}
"""

        result = create_jira_ticket(summary, description)

        if result is not None:
            # Record into state dictionary
            state[pr_key] = {
                "repository": repository,
                "pr": pr_number,
                "prTitle": pr_title,
                "prUrl": pr_url,
                "jiraKey": result.get("key"),
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
            state_updated = True
            print(f"✅ State recorded for {pr_key}")

        if state_updated:
            save_state(STATE_FILE, state)
            print(f"\nState successfully saved to {STATE_FILE}")
        else:
            print("\nNo new Jira tickets were created during this run.")


if __name__ == "__main__":
    main()
