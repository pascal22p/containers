# Renovate to Jira Automation

Automates dependency updates using Renovate and synchronises created Pull Requests with Jira.

**Workflow:**
1. Renovate runs in Docker, scans repositories and creates Pull Requests.
2. A Python script reads Renovate logs, validates open PRs against GitHub, and creates or updates corresponding Jira tickets while preventing duplicates.

## Requirements

- Docker & Docker Compose
- Python 3.10+
- Python packages: `requests`, `pyyaml`

Install dependencies:

```bash
pip install requests PyYAML
```

## Configuration

Configure the following environment variables (e.g. in a `.env` file):

| Variable | Default | Description |
|---|---|---|
| `JIRA_URL` | `https://your-domain.atlassian.net` | Jira instance URL |
| `JIRA_EMAIL` | — | Jira account email |
| `JIRA_BEARER_TOKEN` | — | Jira API bearer token |
| `PROJECT_KEY` | `PROJ` | Target Jira project |
| `ISSUE_TYPE` | `Task` | Jira issue type |
| `JIRA_EPIC` | — | Jira epic ticket, if applicable |
| `JIRA_EPIC_KEY` | — | Epic key to associate tickets with |
| `JIRA_LABELS` | — | Comma-separated Jira labels (e.g. `renovate,automation`) |
| `GITHUB_TOKEN` | — | GitHub token (required for private repositories) |
| `RENOVATE_GIT_PRIVATE_KEY` | — | Base64-encoded GPG private key |
| `RENOVATE_LOG_FILE` | `renovate/renovate.log` | Renovate log file |
| `HOURS_LOOKBACK` | `6` | Log lookback window in hours |
| `STATE_FILE` | `last_jira_pr.json` | Local state file |

## GPG Setup

Renovate uses GPG to sign commits.

1. Generate a key:

   ```bash
   gpg --full-generate-key
   ```

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

## Usage

**1. Run Renovate:**

```bash
docker compose run --rm renovate
```

**2. Synchronise PRs with Jira:**

```bash
python create_jira_tickets.py
```

Run without making Jira changes:

```bash
python create_jira_tickets.py --dry-run
```

The script validates open PRs and creates or updates their associated Jira tickets. Local state is maintained in `last_jira_pr.json` (or the configured `STATE_FILE`) to track PR-to-Jira associations.