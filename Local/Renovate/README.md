# Renovate to Jira Automation Script

This automation operates in two stages:
1. **Renovate:** Runs locally via Docker to scan repositories and open Pull Requests.
2. **Python Automation Script:** Parses Renovate logs, validates open PRs against GitHub, and creates corresponding Jira tickets while preventing duplicates.

---

## Requirements

* **Docker & Docker Compose**
* **Python 3.10+**
* **Python Libraries:** `requests`, `pyyaml`

To install the required Python packages:
    pip install requests PyYAML

---

## Configuration

Set the following environment variables before running the script (or add them to a `.env` file):

- `JIRA_URL` *(Default: `https://your-domain.atlassian.net`)* - Your Jira instance base URL
- `JIRA_EMAIL` - Email address associated with your Jira account
- `JIRA_BEARER_TOKEN` **(Required)** - Personal Access Token or Bearer token for Jira API authentication
- `PROJECT_KEY` *(Default: `PROJ`)* - Target Jira project key
- `ISSUE_TYPE` *(Default: `Task`)* - Jira issue type (e.g., `Task`, `Bug`, `Story`)
- `GITHUB_TOKEN` *(Optional)* - GitHub token (required for private repositories)
- `RENOVATE_GIT_PRIVATE_KEY` - Base64-encoded GPG private key used to sign commits (see guide below)
- `RENOVATE_LOG_FILE` *(Default: `renovate/renovate.log`)* - Path to the Renovate log file
- `HOURS_LOOKBACK` *(Default: `6`)* - Time window to scan for log entries
- `STATE_FILE` *(Default: `last_jira_pr.json`)* - Local state file path

---

## Setting Up GPG Key Signing for Renovate

Renovate requires a GPG key to sign commits. Follow these steps to generate and configure yours:

### 1. Generate the GPG Key
Run the following command in your terminal:
    gpg --full-generate-key

* **Kind of key:** Choose `10` (ECC - sign only).
* **Curve:** Choose `Ed25519` (if offered).
* **Expiration:** Choose `0` for no expiration (or set a preferred timeline).
* **Name:** `Renovate Bot`
* **Email:** Use the email address associated with your GitHub account.
* **Passphrase:** Leave it empty (press Enter).

### 2. Export the Private Key (for Docker)
Export your secret key as ASCII armor:
    gpg --armor --export-secret-keys YOUR_KEY_ID > renovate-private-key.asc

Convert the private key to **Base64** and assign it to your `RENOVATE_GIT_PRIVATE_KEY` environment variable:
    base64 < renovate-private-key.asc | tr -d '\n'

### 3. Export and Register the Public Key (with GitHub)
Export your public key:
    gpg --armor --export YOUR_KEY_ID

Copy the entire output (including `-----BEGIN PGP PUBLIC KEY BLOCK-----` and `-----END PGP PUBLIC KEY BLOCK-----`).

Navigate to **GitHub → Settings → SSH and GPG keys → New GPG key**, paste the block, and save it. *Ensure the email address tied to the GPG key matches your GitHub account.*

---

## Workflow & Usage

### Step 1: Run Renovate via Docker Compose
Run Renovate to scan your repositories and generate the log file containing the PR creation entries.

Execute the container using Docker Compose:
    docker compose run --rm renovate

### Step 2: Run the Python Script
Once Renovate has completed and outputted the log file to `renovate/renovate.log`, execute the script to sync the new PRs to Jira:
    python create_jira_tickets.py
