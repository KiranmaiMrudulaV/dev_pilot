# SDLC Agent Platform

An AI-powered platform that assists developers across the software delivery lifecycle. Five specialized agents analyze GitHub repositories and surface actionable insights — from pull request security review to production incident analysis.

---

## What It Does

| Agent | Description |
|---|---|
| **PR Review** | Analyzes a pull request diff for bugs, security vulnerabilities, and code quality issues |
| **Test Generation** | Reads a source file and automatically writes pytest tests covering happy path, edge cases, and security scenarios |
| **CI/CD Verification** | Fetches recent GitHub Actions workflow runs and explains failures in plain English |
| **Deployment Monitor** | Analyzes deployment history across environments and identifies failure patterns |
| **Incident Analysis** | Given an incident description, investigates recent commits, open issues, and deployments to identify the root cause |

---

## Tech Stack

- **Python** — core language
- **Anthropic Claude API** — AI model powering all agents (Claude Haiku 4.5)
- **GitHub REST API** — source of all data (PRs, commits, CI runs, deployments, issues)
- **Flask** — web interface
- **pytest** — used in generated tests

---

## Project Structure

```
sdlc-agent-platform/
├── app/
│   ├── agents/
│   │   ├── pr_review_agent.py
│   │   ├── test_gen_agent.py
│   │   ├── cicd_agent.py
│   │   ├── deployment_agent.py
│   │   └── incident_agent.py
│   ├── tools/
│   │   └── github_tool.py
│   ├── templates/
│   │   └── index.html
│   └── main.py
├── .env
└── requirements.txt
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/KiranmaiMrudulaV/dev_pilot.git
cd sdlc-agent-platform
```

**2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install anthropic python-dotenv requests flask
```

**4. Add API keys**

Create a `.env` file in the root:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
GITHUB_TOKEN=your-github-token
```

- Anthropic API key: [console.anthropic.com](https://console.anthropic.com)
- GitHub token: GitHub → Settings → Developer settings → Personal access tokens
  - Required scopes: `public_repo`, `repo:status`, `repo_deployment`

**5. Run the app**
```bash
python -m app.main
```

Open `http://127.0.0.1:5000` in your browser.

---

## How It Works

Each agent follows the same pattern — an **agent loop**:

```
1. Send goal to Claude with available tools
2. Claude decides which tool to call
3. Your code executes the tool (GitHub API call)
4. Result is sent back to Claude
5. Claude analyzes the data and returns a response
```

Claude decides on its own which tools to call and in what order based on the goal. You never hardcode the logic — just describe what each tool does and Claude figures out the rest.

---

## Example Usage

**PR Review**
- Repo: `psf/requests`
- PR Number: any open PR from `github.com/psf/requests/pulls`

**Test Generation**
- Repo: `psf/requests`
- File: `requests/auth.py`
- Branch: `main`

**Incident Analysis**
- Repo: `your-org/your-repo`
- Incident: `"Production is down. Users reporting 500 errors since the last deployment."`

---

## Cost

All agents use **Claude Haiku 4.5** — the most cost-efficient Claude model.

| Operation | Estimated Cost |
|---|---|
| PR Review | ~$0.001 |
| Test Generation | ~$0.002 |
| CI/CD Verification | ~$0.001 |
| Deployment Monitor | ~$0.001 |
| Incident Analysis | ~$0.002 |

Entire development and testing phase: under $1.00.

---

## License

MIT
