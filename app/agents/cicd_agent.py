import os
from dotenv import load_dotenv
import anthropic
from app.tools.github_tool import get_workflow_runs, get_run_logs

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [
    {
        "name": "get_workflow_runs",
        "description": "Get recent CI/CD workflow runs for a GitHub repo",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"},
                "limit": {"type": "integer", "description": "Number of runs to fetch, default 5"}
            },
            "required": ["repo"]
        }
    },
    {
        "name": "get_run_logs",
        "description": "Get the logs for a specific workflow run to see why it failed",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"},
                "run_id": {"type": "integer", "description": "The workflow run ID"}
            },
            "required": ["repo", "run_id"]
        }
    }
]

def run_cicd_agent(repo: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"Check the recent CI/CD workflow runs for {repo}. "
                f"Find any failed runs, fetch their logs, and explain in plain English "
                f"what failed and how to fix it. Be concise."
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

                if block.name == "get_workflow_runs":
                    result = get_workflow_runs(
                        repo=block.input["repo"],
                        limit=block.input.get("limit", 5)
                    )
                elif block.name == "get_run_logs":
                    result = get_run_logs(
                        repo=block.input["repo"],
                        run_id=block.input["run_id"]
                    )
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
    report = run_cicd_agent("KiranmaiMrudulaV/sdlc-test-repo")
    print(report)
