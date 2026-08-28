import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from code_executor import execute_python_code

# Load environment variables
load_dotenv()

# Initialize client
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL")
)


def extract_constraints(problem: str) -> str:
    """Tool 1: Extract key constraints from problem statement"""

    prompt = f"""You are analyzing a LeetCode problem. Extract the key constraints and requirements.

PROBLEM: {problem}

List the important constraints:
1. Input constraints (size, range, format)
2. Output requirements (what should be returned, format)
3. Special conditions (edge cases, no extra space, in-place modification, etc.)

Be concise, list only the critical constraints."""

    message = client.messages.create(
        model="claude-sonnet-4.6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def analyze_code_patterns(code: str) -> str:
    """Tool 2: Analyze code structure and patterns that often cause bugs"""

    prompt = f"""Analyze this code for common bug patterns. Look for:

CODE:
{code}

Check for:
1. Loop conditions and bounds (off-by-one errors?)
2. Pointer/index management (left, right, i, j movements)
3. Comparison operators (>, >=, <, <=, ==, !=)
4. Data structure updates (are elements being added/modified correctly?)
5. Return statements (returning correct values?)
6. Edge cases (empty, single element, duplicates)

List potential issues or suspicious patterns."""

    message = client.messages.create(
        model="claude-sonnet-4.6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def debug_code_solution(code: str, problem: str, test_failure: str) -> dict:
    """
    Agent solution: Uses tools to debug more systematically
    """

    # Step 1: Extract constraints
    print("  → Extracting constraints...")
    constraints = extract_constraints(problem)

    # Step 2: Analyze code patterns
    print("  → Analyzing code patterns...")
    patterns = analyze_code_patterns(code)

    # Step 3: EXECUTE CODE LOCALLY (new!)
    print("  → Executing code locally...")
    # Parse test_input and expected output from test_failure
    # Simple extraction: assume "Expected [X], Got [Y]" format
    import re
    match = re.search(r'Expected\s+(.+?),\s+Got', test_failure)
    expected = match.group(1) if match else "unknown"

    # Extract input from test_failure (simple parsing)
    input_match = re.search(r'Input:\s*(.+?)\.\s+Expected', test_failure)
    test_input = input_match.group(1) if input_match else ""

    execution_result = execute_python_code(code, test_input, expected)
    execution_details = f"Execution: {execution_result['details']}\nActual output: {execution_result.get('actual', 'N/A')}"

    # Step 4: Synthesize debugging analysis WITH execution data
    synthesis_prompt = f"""You are an expert debugging assistant. Analyze this code:

PROBLEM: {problem}

CODE:
{code}

TEST FAILURE: {test_failure}

PROBLEM CONSTRAINTS:
{constraints}

CODE PATTERN ANALYSIS:
{patterns}

ACTUAL EXECUTION RESULT:
{execution_details}

Given the above analysis AND real execution data:
1. Identify the specific bug in the code
2. Explain WHY it's a bug (reference constraints and execution output)
3. Suggest the fix (1-2 lines)

Be precise and concise."""

    message = client.messages.create(
        model="claude-sonnet-4.6",
        max_tokens=800,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )

    return {
        "bug_analysis": message.content[0].text,
        "constraints": constraints,
        "patterns": patterns,
        "execution": execution_result
    }


# Test it
if __name__ == "__main__":
    import json

    # Load first test case
    with open('test_cases.json', 'r') as f:
        cases = json.load(f)
        case = cases[0]

    print("Testing SOLUTION on first case:")
    print(f"Problem: {case['problem']}")
    print(f"Expected bug: {case['expected_bug']}\n")

    result = debug_code_solution(case["code"], case["problem"], case["test_failure"])

    print("SOLUTION OUTPUT:")
    print("=" * 60)
    print(result["bug_analysis"])
    print("=" * 60)
    print("\nConstraints extracted:")
    print(result["constraints"][:300])
    print("\nCode patterns analyzed:")
    print(result["patterns"][:300])