import os
from dotenv import load_dotenv
import anthropic
from app.tools.github_tool import get_pr_diff

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [
    {
        "name": "get_pr_diff",
        "description": "Get the code diff for a pull request from GitHub",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"},
                "pr_number": {"type": "integer", "description": "The pull request number"}
            },
            "required": ["repo", "pr_number"]
        }
    }
]

def run_pr_review_agent(repo: str, pr_number: int) -> str:
    messages = [
        {"role": "user", "content": f"Review PR #{pr_number} in {repo} for bugs and security issues. Be concise."}
    ]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "get_pr_diff":
                    result = get_pr_diff(
                        repo=block.input["repo"],
                        pr_number=block.input["pr_number"]
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
    review = run_pr_review_agent("KiranmaiMrudulaV/sdlc-test-repo", 1)
    print(review)
