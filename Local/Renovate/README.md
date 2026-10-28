# Renovate to Jira Automation Script

The feature comes in 2 parts:
- Renovate running locally to raise the pull requests
- A python script to raise Jira tickets for each pull requests

---

## Requirements

* docker compose
* Python 3.10+
* Python libraries: requests, yaml

To install requirements:
    pip install requests, yaml

---

## Configuration

Set the following environment variables before running the script:

- JIRA_URL (Default: https://your-domain.atlassian.net) - Your Jira instance base URL
- JIRA_BEARER_TOKEN (Required) - Personal Access Token or Bearer token for Jira API authentication
- GITHUB_TOKEN (Optional) - GitHub token (required for private repositories)
- PROJECT_KEY (Default: PROJ) - Target Jira project key
- ISSUE_TYPE (Default: Task) - Jira issue type (e.g., Task, Bug, Story)
- RENOVATE_LOG_FILE (Default: renovate/renovate.log) - Path to the Renovate log file
- HOURS_LOOKBACK (Default: 6) - Time window to scan for log entries
- STATE_FILE (Default: last_jira_pr.json) - Local state file path

---

## Workflow & Usage

### Step 1: Run Renovate via Docker Compose
Before running the Python script, run Renovate to generate the log file containing the PR creation entries.

Use the included `docker-compose.yml` configuration.

Run the container using Docker Compose:
    docker compose run --rm renovate

### Step 2: Run the Python Script
Once Renovate has completed and outputted the log file to `renovate/renovate.log`, execute the script:
    python create_jira_tickets.py
    
