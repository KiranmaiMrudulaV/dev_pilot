import os
from dotenv import load_dotenv
import anthropic
from app.tools.github_tool import get_file_contents

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

tools = [
    {
        "name": "get_file_contents",
        "description": "Get the contents of a source code file from a GitHub repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "GitHub repo in format owner/repo"},
                "file_path": {"type": "string", "description": "Path to the file in the repo"},
                "branch": {"type": "string", "description": "Branch name, defaults to main"}
            },
            "required": ["repo", "file_path"]
        }
    }
]

def run_test_gen_agent(repo: str, file_path: str, branch: str = "feature/auth-service") -> str:
    messages = [
        {
            "role": "user",
            "content": (
                f"Read the file '{file_path}' from the '{branch}' branch of {repo}. "
                f"Then write comprehensive pytest tests for it. "
                f"Include tests for happy path, edge cases, and security vulnerabilities. "
                f"Return only the test code, no explanation."
            )
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
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
                if block.name == "get_file_contents":
                    result = get_file_contents(
                        repo=block.input["repo"],
                        file_path=block.input["file_path"],
                        branch=block.input.get("branch", branch)
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
    tests = run_test_gen_agent(
        repo="KiranmaiMrudulaV/sdlc-test-repo",
        file_path="auth.py"
    )
    print(tests)
