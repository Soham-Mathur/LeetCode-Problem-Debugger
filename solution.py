import os
import json
import time
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

# ============================================================================
# API PRICING CONSTANTS (Haiku)
# ============================================================================
PRICING = {
    "input_tokens_per_1m": 0.80,  # $0.80 per 1M input tokens
    "output_tokens_per_1m": 4.00,  # $4.00 per 1M output tokens
}


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate API cost for tokens used"""
    input_cost = (input_tokens / 1_000_000) * PRICING["input_tokens_per_1m"]
    output_cost = (output_tokens / 1_000_000) * PRICING["output_tokens_per_1m"]
    return input_cost + output_cost


# ============================================================================
# TOOL RETURN SIGNATURE: StandardToolReturn
# ============================================================================
def create_tool_return(output: str, input_tokens: int, output_tokens: int, latency_sec: float) -> dict:
    """Standardized tool return with metrics"""
    return {
        "output": output,
        "metrics": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "latency_sec": latency_sec,
            "cost_usd": calculate_cost(input_tokens, output_tokens)
        }
    }


def validate_inputs(code: str, problem: str) -> tuple[bool, str]:
    """Validate inputs before processing"""
    if not code or not isinstance(code, str):
        return False, "Error: Code is empty or invalid"
    if not problem or not isinstance(problem, str):
        return False, "Error: Problem description is empty or invalid"
    if len(code) < 10:
        return False, "Error: Code snippet too short"
    if len(problem) < 5:
        return False, "Error: Problem description too short"
    return True, "Valid"


def extract_constraints(problem: str) -> dict:
    """Tool 1: Extract constraints - WITH METRICS"""

    tool_start = time.time()

    try:
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

        latency = time.time() - tool_start
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

        return create_tool_return(message.content[0].text, input_tokens, output_tokens, latency)

    except Exception as e:
        latency = time.time() - tool_start
        error_msg = f"[Error: {str(e)[:50]}]"
        return create_tool_return(error_msg, 0, 0, latency)


def analyze_code_patterns(code: str) -> dict:
    """Tool 2: Analyze patterns - WITH METRICS"""

    tool_start = time.time()

    try:
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

        latency = time.time() - tool_start
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

        return create_tool_return(message.content[0].text, input_tokens, output_tokens, latency)

    except Exception as e:
        latency = time.time() - tool_start
        error_msg = f"[Error: {str(e)[:50]}]"
        return create_tool_return(error_msg, 0, 0, latency)


def suggest_fix(code: str, bug_description: str, problem: str) -> dict:
    """Tool 3: Suggest fix - WITH METRICS"""

    tool_start = time.time()

    try:
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

        latency = time.time() - tool_start
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

        return create_tool_return(message.content[0].text, input_tokens, output_tokens, latency)

    except Exception as e:
        latency = time.time() - tool_start
        error_msg = f"[Error: {str(e)[:50]}]"
        return create_tool_return(error_msg, 0, 0, latency)


def debug_code_solution(code: str, problem: str, test_failure: str, test_input: str = "",
                        expected_output: str = "") -> dict:
    """
    Agent solution: Uses 3 tools with COMPREHENSIVE METRICS TRACKING
    """

    case_start = time.time()

    # Initialize accumulators
    total_input_tokens = 0
    total_output_tokens = 0
    total_latency = 0
    tool_metrics = {}

    # Step 0: Validate inputs
    valid, msg = validate_inputs(code, problem)
    if not valid:
        return {
            "bug_analysis": f"Error: {msg}",
            "constraints": "N/A",
            "patterns": "N/A",
            "bug_identified": "N/A",
            "fix_suggested": "N/A",
            "execution": None,
            "execution_details": "Input validation failed",
            "error": msg,
            "metrics": {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "total_latency_sec": time.time() - case_start,
                "total_cost_usd": 0.0,
                "tool_breakdown": {}
            }
        }

    # Step 1: Extract constraints
    print("  → Tool 1: Extracting constraints...")
    try:
        tool1_result = extract_constraints(problem)
        constraints = tool1_result["output"]
        tool_metrics["tool_1_constraints"] = tool1_result["metrics"]
        total_input_tokens += tool1_result["metrics"]["input_tokens"]
        total_output_tokens += tool1_result["metrics"]["output_tokens"]
        total_latency += tool1_result["metrics"]["latency_sec"]
    except Exception as e:
        constraints = f"[Error: {str(e)[:50]}]"
        tool_metrics["tool_1_constraints"] = {"error": str(e)[:50]}

    # Step 2: Analyze code patterns
    print("  → Tool 2: Analyzing code patterns...")
    try:
        tool2_result = analyze_code_patterns(code)
        patterns = tool2_result["output"]
        tool_metrics["tool_2_patterns"] = tool2_result["metrics"]
        total_input_tokens += tool2_result["metrics"]["input_tokens"]
        total_output_tokens += tool2_result["metrics"]["output_tokens"]
        total_latency += tool2_result["metrics"]["latency_sec"]
    except Exception as e:
        patterns = f"[Error: {str(e)[:50]}]"
        tool_metrics["tool_2_patterns"] = {"error": str(e)[:50]}

    # Step 3: Execute code
    print("  → Getting real execution data...")
    execution_result = None
    execution_details = "No execution data available"

    try:
        if test_input and expected_output:
            execution_result = execute_python_code(code, test_input, expected_output)
            if execution_result["success"]:
                execution_details = f"✅ Test Passed: Output is {execution_result['actual']}"
            else:
                execution_details = f"❌ Test Failed:\n  Expected: {execution_result['expected']}\n  Actual: {execution_result['actual']}\n  Error: {execution_result['details']}"
        else:
            try:
                parsed_input, parsed_expected = parse_test_failure(test_failure)
                if parsed_input and parsed_expected:
                    execution_result = execute_python_code(code, parsed_input, parsed_expected)
                    if execution_result["success"]:
                        execution_details = f"✅ Test Passed: Output is {execution_result['actual']}"
                    else:
                        execution_details = f"❌ Test Failed:\n  Expected: {execution_result['expected']}\n  Actual: {execution_result['actual']}\n  Error: {execution_result['details']}"
            except Exception as e:
                execution_details = f"[Could not parse: {str(e)[:50]}]"
    except Exception as e:
        execution_details = f"[Execution error: {str(e)[:50]}]"

    # Step 4: Preliminary bug identification
    print("  → Identifying bug location...")
    bug_description = ""
    tool4_start = time.time()
    try:
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
        step4_latency = time.time() - tool4_start
        tool_metrics["tool_3_bug_id"] = {
            "input_tokens": prelim_message.usage.input_tokens,
            "output_tokens": prelim_message.usage.output_tokens,
            "total_tokens": prelim_message.usage.input_tokens + prelim_message.usage.output_tokens,
            "latency_sec": step4_latency,
            "cost_usd": calculate_cost(prelim_message.usage.input_tokens, prelim_message.usage.output_tokens)
        }
        total_input_tokens += prelim_message.usage.input_tokens
        total_output_tokens += prelim_message.usage.output_tokens
        total_latency += step4_latency
    except Exception as e:
        bug_description = f"[Error: {str(e)[:50]}]"
        tool_metrics["tool_3_bug_id"] = {"error": str(e)[:50]}

    # Step 5: Suggest fix
    print("  → Tool 4: Suggesting fix...")
    try:
        tool4_result = suggest_fix(code, bug_description, problem)
        fix_suggestion = tool4_result["output"]
        tool_metrics["tool_4_fix"] = tool4_result["metrics"]
        total_input_tokens += tool4_result["metrics"]["input_tokens"]
        total_output_tokens += tool4_result["metrics"]["output_tokens"]
        total_latency += tool4_result["metrics"]["latency_sec"]
    except Exception as e:
        fix_suggestion = f"[Error: {str(e)[:50]}]"
        tool_metrics["tool_4_fix"] = {"error": str(e)[:50]}

    # Step 6: Final synthesis
    print("  → Tool 5: Synthesizing final analysis...")
    try:
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

        final_analysis = message.content[0].text
        tool_metrics["tool_5_synthesis"] = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
            "total_tokens": message.usage.input_tokens + message.usage.output_tokens,
            "cost_usd": calculate_cost(message.usage.input_tokens, message.usage.output_tokens)
        }
        total_input_tokens += message.usage.input_tokens
        total_output_tokens += message.usage.output_tokens
    except Exception as e:
        final_analysis = f"[Synthesis failed: {str(e)[:100]}]"
        tool_metrics["tool_5_synthesis"] = {"error": str(e)[:50]}

    # Calculate totals
    total_tokens = total_input_tokens + total_output_tokens
    total_cost = calculate_cost(total_input_tokens, total_output_tokens)
    case_latency = time.time() - case_start

    return {
        "bug_analysis": final_analysis,
        "constraints": constraints,
        "patterns": patterns,
        "bug_identified": bug_description,
        "fix_suggested": fix_suggestion,
        "execution": execution_result,
        "execution_details": execution_details,
        "metrics": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "total_latency_sec": case_latency,
            "total_cost_usd": total_cost,
            "tool_breakdown": tool_metrics
        }
    }


# Test it
if __name__ == "__main__":
    import json

    # Load first test case
    with open('test_cases.json', 'r') as f:
        cases = json.load(f)
        case = cases[0]

    print("Testing SOLUTION (with metrics) on first case:")
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

    print("\n" + "=" * 60)
    print("METRICS SUMMARY:")
    print("=" * 60)
    metrics = result["metrics"]
    print(
        f"Total Tokens: {metrics['total_tokens']} (Input: {metrics['total_input_tokens']}, Output: {metrics['total_output_tokens']})")
    print(f"Total Latency: {metrics['total_latency_sec']:.2f}s")
    print(f"Total Cost: ${metrics['total_cost_usd']:.4f}")
    print(f"\nPer-Tool Breakdown:")
    for tool, tool_metrics in metrics['tool_breakdown'].items():
        if 'total_tokens' in tool_metrics:
            print(f"  {tool}: {tool_metrics['total_tokens']} tokens, ${tool_metrics['cost_usd']:.4f}")