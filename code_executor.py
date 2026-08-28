import subprocess
import sys
import re


def extract_function_name(code_str: str) -> str:
    """Extract function name from code"""
    match = re.search(r'def\s+(\w+)\s*\(', code_str)
    if match:
        return match.group(1)
    return None


def parse_test_failure(test_failure: str) -> tuple:
    """Extract test input and expected output from test failure string"""

    test_input = ""
    expected = ""

    # Try multiple patterns for input extraction
    patterns = [
        r'Input:\s*(.+?)\.\s*Expected',  # "Input: X. Expected"
        r'Input:\s*(.+?),\s*Expected',  # "Input: X, Expected"
        r'Input:\s*(.+?)$',  # "Input: X" at end
    ]

    for pattern in patterns:
        match = re.search(pattern, test_failure)
        if match:
            test_input = match.group(1).strip()
            break

    # Try multiple patterns for expected extraction
    expected_patterns = [
        r'Expected\s+(.+?),\s*Got',  # "Expected X, Got"
        r'Expected\s+(.+?)\.',  # "Expected X."
        r'Expected:\s*(.+?),',  # "Expected: X,"
    ]

    for pattern in expected_patterns:
        match = re.search(pattern, test_failure)
        if match:
            expected = match.group(1).strip()
            break

    return test_input, expected


def execute_python_code(code_str: str, test_input: str, expected_output: str) -> dict:
    """
    Executes Python code safely via subprocess and returns execution details.

    Args:
        code_str: Python function code (string)
        test_input: Input arguments (e.g., "[3, 3], 6" for twoSum)
        expected_output: Expected output (e.g., "[0, 1]")

    Returns:
        dict with execution status and details
    """

    # Extract function name from code
    func_name = extract_function_name(code_str)
    if not func_name:
        return {
            "success": False,
            "error_type": "Parse Error",
            "details": "Could not extract function name from code",
            "actual": "N/A"
        }

    # Build the runner script
    runner_script = f"""
{code_str}

if __name__ == '__main__':
    try:
        result = {func_name}({test_input})
        print("ACTUAL_OUTPUT:", result)
    except Exception as e:
        print("ERROR:", type(e).__name__, ":", str(e))
"""

    try:
        # Execute with safety guardrails
        process = subprocess.run(
            [sys.executable, "-c", runner_script],
            capture_output=True,
            text=True,
            timeout=2  # Max 2 seconds
        )

        stdout = process.stdout[:500]  # Max 500 chars
        stderr = process.stderr[:500]

        # Check for ERROR in output
        if "ERROR:" in stdout:
            error_line = [line for line in stdout.split('\n') if 'ERROR:' in line]
            error_msg = error_line[0].replace("ERROR:", "").strip() if error_line else "Unknown error"
            return {
                "success": False,
                "error_type": "Runtime Error",
                "details": error_msg,
                "actual": "ERROR"
            }

        # Check process return code
        if process.returncode != 0:
            return {
                "success": False,
                "error_type": "Execution Failed",
                "details": stderr if stderr else "Process returned non-zero exit code",
                "actual": "ERROR"
            }

        # Parse actual output
        actual_output = stdout.strip()
        if "ACTUAL_OUTPUT:" in actual_output:
            actual_output = actual_output.split("ACTUAL_OUTPUT:")[-1].strip()

        # Compare with expected
        passed = str(actual_output) == str(expected_output)

        return {
            "success": passed,
            "expected": str(expected_output),
            "actual": actual_output,
            "details": "✅ Test Passed" if passed else "❌ Output Mismatch",
            "stdout": stdout
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "TimeoutError",
            "details": "Code execution exceeded 2-second limit (infinite loop?)",
            "actual": "TIMEOUT"
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": "Execution Error",
            "details": str(e),
            "actual": "ERROR"
        }


# Test it
if __name__ == "__main__":
    import json

    print("=" * 80)
    print("TESTING CODE EXECUTOR")
    print("=" * 80)

    try:
        with open('test_cases.json', 'r') as f:
            test_cases = json.load(f)

        # Test first 5 cases
        for case in test_cases[:5]:
            print(f"\n[Case {case['id']}] {case['problem']}")

            # Use test_input and expected_output directly from JSON
            test_input = case['test_input']
            expected = case['expected_output']

            print(f"  Input: {test_input}")
            print(f"  Expected: {expected}")

            # Execute
            result = execute_python_code(case['code'], test_input, expected)
            print(f"  Actual: {result['actual']}")
            print(f"  Status: {result['details']}")

    except FileNotFoundError:
        print("\n⚠️ test_cases.json not found.")