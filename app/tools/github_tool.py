import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

def get_pr_diff(repo: str, pr_number: int) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        return f"Error fetching PR: {response.status_code} - {response.text}"

def get_file_contents(repo: str, file_path: str, branch: str = "main") -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers_json)

    if response.status_code == 200:
        import base64
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")
    else:
        return f"Error fetching file: {response.status_code}"

def get_deployments(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}/deployments"
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers_json)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    deployments = response.json()
    if not deployments:
        return "No deployments found for this repo."

    output = []
    for d in deployments[:10]:
        statuses_url = f"https://api.github.com/repos/{repo}/deployments/{d['id']}/statuses"
        statuses_response = requests.get(statuses_url, headers=headers_json)
        latest_status = "unknown"
        if statuses_response.status_code == 200:
            statuses = statuses_response.json()
            if statuses:
                latest_status = statuses[0]["state"]
        output.append(
            f"id={d['id']} | env={d.get('environment','unknown')} | "
            f"status={latest_status} | created={d['created_at']} | sha={d['sha'][:7]}"
        )
    return "\n".join(output)

def create_test_deployment(repo: str, environment: str, state: str) -> str:
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    deploy_response = requests.post(
        f"https://api.github.com/repos/{repo}/deployments",
        headers=headers_json,
        json={"ref": "main", "environment": environment, "auto_merge": False,
              "required_contexts": []}
    )
    if deploy_response.status_code not in (201, 202):
        return f"Error creating deployment: {deploy_response.status_code} {deploy_response.text}"

    deploy_id = deploy_response.json()["id"]
    requests.post(
        f"https://api.github.com/repos/{repo}/deployments/{deploy_id}/statuses",
        headers=headers_json,
        json={"state": state}
    )
    return f"Created deployment {deploy_id} in {environment} with state={state}"

def get_recent_commits(repo: str, limit: int = 10) -> str:
    url = f"https://api.github.com/repos/{repo}/commits?per_page={limit}"
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers_json)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    commits = response.json()
    output = []
    for c in commits:
        sha = c["sha"][:7]
        message = c["commit"]["message"].split("\n")[0]
        author = c["commit"]["author"]["name"]
        date = c["commit"]["author"]["date"]
        output.append(f"{sha} | {date} | {author} | {message}")
    return "\n".join(output)

def get_open_issues(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}/issues?state=open"
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers_json)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    issues = response.json()
    if not issues:
        return "No open issues found."

    output = []
    for i in issues:
        output.append(f"#{i['number']} | {i['title']} | opened={i['created_at']}")
    return "\n".join(output)

def get_workflow_runs(repo: str, limit: int = 5) -> str:
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page={limit}"
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers_json)

    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        result = []
        for r in runs:
            result.append(f"run_id={r['id']} | {r['name']} | status={r['status']} | conclusion={r['conclusion']} | created={r['created_at']}")
        return "\n".join(result)
    return f"Error: {response.status_code}"

def get_run_logs(repo: str, run_id: int) -> str:
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    jobs_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
    jobs_response = requests.get(jobs_url, headers=headers_json)

    if jobs_response.status_code != 200:
        return f"Error fetching jobs: {jobs_response.status_code}"

    jobs = jobs_response.json().get("jobs", [])
    output = []

    for job in jobs:
        output.append(f"Job: {job['name']} — {job['conclusion']}")
        for step in job.get("steps", []):
            icon = "✅" if step["conclusion"] == "success" else "❌"
            output.append(f"  {icon} {step['name']} — {step['conclusion']}")

        log_url = f"https://api.github.com/repos/{repo}/actions/jobs/{job['id']}/logs"
        log_response = requests.get(log_url, headers=headers_json, allow_redirects=True)
        if log_response.status_code == 200:
            output.append("--- LOGS ---")
            output.append(log_response.text[-2000:])

    return "\n".join(output)

def get_pr_files(repo: str, pr_number: int) -> list:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers_json = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers_json)

    if response.status_code == 200:
        return response.json()
    else:
        return []
