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

    # Try to extract input - looks for "Input: [something]. Expected"
    input_match = re.search(r'Input:\s*(.+?)\.\s*Expected', test_failure)
    test_input = input_match.group(1).strip() if input_match else ""

    # Try to extract expected output - looks for "Expected [X], Got"
    expected_match = re.search(r'Expected\s+(.+?),\s*Got', test_failure)
    expected = expected_match.group(1).strip() if expected_match else ""

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

    # Test 1: Load and test from test_cases.json
    print("=" * 80)
    print("TESTING CODE EXECUTOR")
    print("=" * 80)

    try:
        with open('test_cases.json', 'r') as f:
            test_cases = json.load(f)

        # Test first 3 cases
        for case in test_cases[:3]:
            print(f"\n[Case {case['id']}] {case['problem']}")

            # Parse test failure
            test_input, expected = parse_test_failure(case['test_failure'])
            print(f"  Input: {test_input}")
            print(f"  Expected: {expected}")

            # Execute
            result = execute_python_code(case['code'], test_input, expected)
            print(f"  Actual: {result['actual']}")
            print(f"  Status: {result['details']}")

    except FileNotFoundError:
        print("\n⚠️ test_cases.json not found. Testing with hardcoded example instead...\n")

        # Hardcoded test
        code = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

        print("Testing twoSum (correct code):")
        result = execute_python_code(code, "[2, 7, 11, 15], 9", "[0, 1]")
        print(f"  Result: {result}")

        print("\nTesting twoSum (buggy code):")
        code_buggy = """
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
        result = execute_python_code(code_buggy, "[3, 3], 6", "[0, 1]")
        print(f"  Result: {result}")