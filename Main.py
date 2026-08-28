import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

# Initialize client using your relay credentials
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL")
)


def debug_code_baseline(code: str, problem: str, test_failure: str) -> str:
    """Simple baseline: ask Claude to debug"""

    prompt = f"""Debug this LeetCode solution:

PROBLEM: {problem}

CODE:
{code}

TEST FAILURE: {test_failure}

What is the bug? Be concise."""

    message = client.messages.create(
        model="claude-sonnet-4.6",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return message.content[0].text


# Test it
if __name__ == "__main__":
    code = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

    problem = "Find two numbers in array that add up to target"
    test_failure = "Input: [2,7,11,15], target=9. Expected [0,1], Got []"

    result = debug_code_baseline(code, problem, test_failure)
    print("BASELINE OUTPUT:")
    print(result)