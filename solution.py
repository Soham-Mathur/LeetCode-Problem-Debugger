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
    """Tool 1: Extract specific, actionable constraints for debugging"""

    prompt = f"""You are analyzing a LeetCode problem to extract debugging-critical constraints.

PROBLEM: {problem}

Extract constraints in these specific categories:

1. **Input Constraints:**
   - Array/string size limits (n, m ranges)
   - Element value ranges (can be negative? zero?)
   - Any special properties (sorted? unique?)

2. **Output Requirements:**
   - What format? (array, int, boolean, etc.)
   - Any ordering requirements?
   - In-place modification or return new?

3. **Critical Logic Rules (Most important for debugging):**
   - Must use different elements? (Two pointers problem)
   - Must preserve order?
   - Must avoid duplicates in result?
   - Time/space complexity hints?
   - Special edge cases to handle?

4. **Common Bug Triggers:**
   - Off-by-one: Any loop bounds that matter?
   - Comparison operators: > vs >=, < vs <=?
   - Pointer management: left/right pointer updates?
   - State changes: When to reset counters/pointers?

Be specific with examples. For instance:
- Instead of "array has elements", say "array has 1-10^5 elements, can include duplicates"
- Instead of "return indices", say "return two DIFFERENT indices [i, j] where i != j"

Format as a numbered list. Be concise but specific."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def analyze_code_patterns(code: str) -> str:
    """Tool 2: Systematically analyze code for bug-prone patterns"""

    prompt = f"""You are analyzing code for debugging patterns. Be systematic and specific.

CODE:
{code}

Check EACH of these categories and report findings:

**1. Loop Conditions & Bounds (Off-by-one errors)**
   - What are all the loops? (for, while)
   - What are their start/end conditions? (range(0, n)? range(i, n)?)
   - Do they correctly include/exclude boundary elements?
   - Common mistakes: range(n) vs range(n+1), left < right vs left <= right

**2. Pointer/Index Management**
   - Are there left/right pointers? left = 0, right = len(x) - 1
   - When do they move? left += 1, right -= 1
   - Do they ever overlap incorrectly?
   - Are indices ever accessed when out of bounds?

**3. Comparison Operators**
   - All == comparisons correct? (should be !=?)
   - All > vs >= correct?
   - All < vs <= correct?
   - Impact on boundary conditions?

**4. State Changes & Updates**
   - When variables are updated (min_price, count, k), is timing correct?
   - Should they be updated before or after checks?
   - Are they updated in all necessary branches?

**5. Return Statements**
   - What gets returned? Is it the right type?
   - Are there paths that don't return?
   - Should it return intermediate results or final?

**6. Edge Cases Not Handled**
   - Empty input? (arrays, strings)
   - Single element?
   - Duplicates?
   - Negative numbers?

For each finding, state:
- WHAT: The potential issue
- WHERE: Line number or code snippet
- WHY: How this could cause a bug
- IMPACT: What output would be wrong

Be concise but thorough."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def suggest_fix(code: str, bug_description: str, problem: str) -> str:
    """Tool 3: Generate precise, testable code fixes"""

    prompt = f"""You are generating a precise code fix based on bug analysis.

PROBLEM: {problem}

BUGGY CODE:
{code}

BUG IDENTIFIED: {bug_description}

Generate a fix by:

1. **Identify exact line(s) to change**
   - Show the original line exactly as it appears
   - Show the corrected line

2. **Explain the change in 1 sentence**
   - Why this specific change fixes the bug
   - What constraint it now satisfies

3. **Verify the fix works**
   - Show how the corrected code would execute
   - Walk through with the failing test case
   - Show the corrected output

4. **Consider side effects**
   - Does this fix break anything else?
   - Does it handle edge cases now?

Format as:

**Line X:** 
```python
# BEFORE:
original_line_here

# AFTER:
fixed_line_here
```

**Why:** One sentence explanation.

**Verification:** Walk through with test case showing correct output.

Be precise. Show exact code, not pseudocode."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def debug_code_solution(code: str, problem: str, test_failure: str, test_input: str = "",
                        expected_output: str = "") -> dict:
    """
    Agent solution: Uses tools to debug more systematically WITH REAL EXECUTION DATA

    Args:
        code: Python function code
        problem: Problem description
        test_failure: Test failure description
        test_input: Input for execution (e.g., "[3, 3], 6")
        expected_output: Expected output (e.g., "[0, 1]")
    """

    # Step 1: Extract constraints
    print("  → Extracting constraints...")
    constraints = extract_constraints(problem)

    # Step 2: Analyze code patterns
    print("  → Analyzing code patterns...")
    patterns = analyze_code_patterns(code)

    # Step 3: EXECUTE CODE TO GET REAL DATA (NEW!)
    print("  → Executing code locally for real data...")
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

    # Step 4: Synthesize debugging analysis WITH REAL EXECUTION DATA
    synthesis_prompt = f"""You are an expert debugging assistant. Analyze this code USING REAL EXECUTION DATA:

PROBLEM: {problem}

CODE:
{code}

TEST FAILURE: {test_failure}

PROBLEM CONSTRAINTS:
{constraints}

CODE PATTERN ANALYSIS:
{patterns}

ACTUAL CODE EXECUTION RESULT:
{execution_details}

Given the above analysis AND real execution data:
1. Identify the specific bug in the code
2. Explain WHY it's a bug (reference the constraints and actual execution results)
3. Suggest the fix (1-2 lines)

Use the actual execution output to confirm your analysis. Be precise and concise."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )

    return {
        "bug_analysis": message.content[0].text,
        "constraints": constraints,
        "patterns": patterns,
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

    print("Testing SOLUTION (with real execution data) on first case:")
    print(f"Problem: {case['problem']}")
    print(f"Expected bug: Case 1 - should catch the bug\n")

    result = debug_code_solution(
        code=case["code"],
        problem=case["problem"],
        test_failure=case["test_failure"],
        test_input=case["test_input"],
        expected_output=case["expected_output"]
    )

    print("SOLUTION OUTPUT:")
    print("=" * 60)
    print(result["bug_analysis"])
    print("=" * 60)
    print("\nExecution details:")
    print(result["execution_details"])