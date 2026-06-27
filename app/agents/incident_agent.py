import os
from dotenv import load_dotenv
import anthropic
from app.tools.github_tool import get_recent_commits, get_open_issues, get_deployments

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [
    {
        "name": "get_recent_commits",
        "description": "Get recent commits to find what code changes were made recently",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"},
                "limit": {"type": "integer", "description": "Number of commits to fetch"}
            },
            "required": ["repo"]
        }
    },
    {
        "name": "get_open_issues",
        "description": "Get open GitHub issues to find known bugs or reported problems",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"}
            },
            "required": ["repo"]
        }
    },
    {
        "name": "get_deployments",
        "description": "Get deployment history to see which deployments succeeded or failed",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"}
            },
            "required": ["repo"]
        }
    }
]

def run_incident_agent(repo: str, incident: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"INCIDENT REPORT: {incident}\n\n"
                f"Repo: {repo}\n\n"
                f"Investigate this incident. Check recent commits, open issues, "
                f"and deployment history. Identify the most likely root cause "
                f"and give a clear action plan. Be concise."
            )
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        if response.stop_reason in ("end_turn", "max_tokens"):
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                if block.name == "get_recent_commits":
                    result = get_recent_commits(
                        repo=block.input["repo"],
                        limit=block.input.get("limit", 10)
                    )
                elif block.name == "get_open_issues":
                    result = get_open_issues(repo=block.input["repo"])
                elif block.name == "get_deployments":
                    result = get_deployments(repo=block.input["repo"])
                else:
                    result = "Unknown tool"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    report = run_incident_agent(
        repo="KiranmaiMrudulaV/sdlc-test-repo",
        incident="Production is down. Users are reporting login failures since the last deployment."
    )
    print(report)
