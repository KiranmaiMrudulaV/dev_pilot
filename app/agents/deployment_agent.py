import os
from dotenv import load_dotenv
import anthropic
from app.tools.github_tool import get_deployments, create_test_deployment

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [
    {
        "name": "get_deployments",
        "description": "Get deployment history for a GitHub repo including status of each deployment",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"}
            },
            "required": ["repo"]
        }
    }
]

def run_deployment_agent(repo: str) -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"Check the deployment history for {repo}. "
                f"Identify any failed or problematic deployments, "
                f"spot any patterns, and recommend what the team should do next. Be concise."
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
                if block.name == "get_deployments":
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


def seed_test_deployments(repo: str):
    print("Creating test deployments...")
    create_test_deployment(repo, "staging", "success")
    create_test_deployment(repo, "staging", "failure")
    create_test_deployment(repo, "production", "failure")
    create_test_deployment(repo, "staging", "success")
    create_test_deployment(repo, "production", "failure")
    print("Done. Now running agent...\n")


if __name__ == "__main__":
    repo = "KiranmaiMrudulaV/sdlc-test-repo"
    seed_test_deployments(repo)
    report = run_deployment_agent(repo)
    print(report)
