import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from code_executor import execute_python_code, parse_test_failure

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
        model="claude-haiku-4-5-20251001",
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
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def suggest_fix(code: str, bug_description: str, problem: str) -> str:
    """Tool 3: Generate code fix based on bug analysis"""

    prompt = f"""Given this buggy code and bug description, suggest a precise fix:

PROBLEM: {problem}

CODE:
{code}

BUG IDENTIFIED: {bug_description}

Provide:
1. The exact line(s) that need to change
2. What to change them to (provide the corrected line)
3. Why this fixes the bug in 1 sentence

Format:
Line X: Change "old_code" to "new_code"
Reason: Brief explanation"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def debug_code_solution(code: str, problem: str, test_failure: str, test_input: str = "",
                        expected_output: str = "") -> dict:
    """
    Agent solution: Uses 3 tools to debug systematically WITH REAL EXECUTION DATA

    Args:
        code: Python function code
        problem: Problem description
        test_failure: Test failure description
        test_input: Input for execution (e.g., "[3, 3], 6")
        expected_output: Expected output (e.g., "[0, 1]")
    """

    # Step 1: Extract constraints
    print("  → Tool 1: Extracting constraints...")
    constraints = extract_constraints(problem)

    # Step 2: Analyze code patterns
    print("  → Tool 2: Analyzing code patterns...")
    patterns = analyze_code_patterns(code)

    # Step 3: EXECUTE CODE TO GET REAL DATA
    print("  → Getting real execution data...")
    execution_result = None
    execution_details = "No execution data available"

    if test_input and expected_output:
        try:
            execution_result = execute_python_code(code, test_input, expected_output)
            if execution_result["success"]:
                execution_details = f"✅ Test Passed: Output is {execution_result['actual']}"
            else:
                execution_details = f"❌ Test Failed:\n  Expected: {execution_result['expected']}\n  Actual: {execution_result['actual']}\n  Error: {execution_result['details']}"
        except Exception as e:
            execution_details = f"Execution error: {str(e)}"
    else:
        # Fallback: try to parse from test_failure
        try:
            parsed_input, parsed_expected = parse_test_failure(test_failure)
            if parsed_input and parsed_expected:
                execution_result = execute_python_code(code, parsed_input, parsed_expected)
                if execution_result["success"]:
                    execution_details = f"✅ Test Passed: Output is {execution_result['actual']}"
                else:
                    execution_details = f"❌ Test Failed:\n  Expected: {execution_result['expected']}\n  Actual: {execution_result['actual']}\n  Error: {execution_result['details']}"
        except:
            pass

    # Step 4: PRELIMINARY BUG IDENTIFICATION (for Tool 3)
    print("  → Identifying bug location...")
    preliminary_analysis_prompt = f"""Briefly identify the bug in this code without fixing it yet:

CODE:
{code}

CONSTRAINTS:
{constraints}

PATTERNS ANALYSIS:
{patterns}

EXECUTION RESULT:
{execution_details}

In 1-2 sentences, what is the bug?"""

    prelim_message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": preliminary_analysis_prompt}]
    )
    bug_description = prelim_message.content[0].text

    # Step 5: Tool 3 - Suggest Fix
    print("  → Tool 3: Suggesting fix...")
    fix_suggestion = suggest_fix(code, bug_description, problem)

    # Step 6: FINAL SYNTHESIS with all tool outputs
    synthesis_prompt = f"""You are an expert debugging assistant. Synthesize the analysis from all tools:

PROBLEM: {problem}

CODE:
{code}

CONSTRAINTS:
{constraints}

CODE PATTERNS:
{patterns}

EXECUTION RESULT:
{execution_details}

BUG IDENTIFIED:
{bug_description}

SUGGESTED FIX:
{fix_suggestion}

Now provide a final, complete debugging analysis:
1. Restate the bug clearly
2. Explain WHY it violates the constraints/logic
3. Confirm the fix resolves it
4. Show the corrected code (1-2 lines)

Be precise and concise."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )

    return {
        "bug_analysis": message.content[0].text,
        "constraints": constraints,
        "patterns": patterns,
        "bug_identified": bug_description,
        "fix_suggested": fix_suggestion,
        "execution": execution_result,
        "execution_details": execution_details
    }


# Test it
if __name__ == "__main__":
    import json

    # Load first test case
    with open('test_cases.json', 'r') as f:
        cases = json.load(f)
        case = cases[0]

    print("Testing SOLUTION (3 Tools) on first case:")
    print(f"Problem: {case['problem']}\n")

    result = debug_code_solution(
        code=case["code"],
        problem=case["problem"],
        test_failure=case["test_failure"],
        test_input=case["test_input"],
        expected_output=case["expected_output"]
    )

    print("\n" + "=" * 60)
    print("FINAL BUG ANALYSIS:")
    print("=" * 60)
    print(result["bug_analysis"])