import os
import json
from dotenv import load_dotenv
from Main import debug_code_baseline

# Load environment variables
load_dotenv()


def score_debug_output(agent_output: str, expected_bug: str) -> bool:
    """
    Score if agent correctly identified the bug.
    Check if output contains key debugging terms.
    """
    keywords = [
        "bug",
        "error",
        "wrong",
        "issue",
        "problem",
        "off-by-one",
        "off by one",
        "index",
        "boundary",
        "condition",
        "should be",
        "increment",
        "decrement",
        "pointer",
        "overwriting",
        "overwrites",
        "forgot",
        "missing",
        "duplicate",
        "sum",
        "calculation",
        "loop",
        "return"
    ]

    output_lower = agent_output.lower()
    match_score = sum(1 for kw in keywords if kw in output_lower)

    # Score >= 3 keywords = probably correct
    return match_score >= 3


def evaluate_baseline():
    """Run baseline on all test cases"""

    # Load test cases
    with open('test_cases.json', 'r') as f:
        test_cases = json.load(f)

    results = {
        "baseline": {
            "correct": 0,
            "total": len(test_cases),
            "cases": []
        }
    }

    print("=" * 80)
    print("EVALUATING BASELINE ON 10 TEST CASES")
    print("=" * 80)

    for case in test_cases:
        problem_id = case["id"]
        problem = case["problem"]
        code = case["code"]
        test_failure = case["test_failure"]
        expected_bug = case["expected_bug"]

        print(f"\n[Case {problem_id}] {problem}")
        print(f"Expected bug: {expected_bug}")

        try:
            output = debug_code_baseline(code, problem, test_failure)
            print(f"Output: {output[:150]}...")

            # Score it
            is_correct = score_debug_output(output, expected_bug)
            results["baseline"]["cases"].append({
                "id": problem_id,
                "problem": problem,
                "correct": is_correct,
                "output": output[:300]
            })

            if is_correct:
                results["baseline"]["correct"] += 1
                print("✅ CORRECT")
            else:
                print("❌ INCORRECT (but captured output)")

        except Exception as e:
            print(f"❌ ERROR: {str(e)[:100]}")
            results["baseline"]["cases"].append({
                "id": problem_id,
                "problem": problem,
                "correct": False,
                "error": str(e)[:200]
            })

    # Print summary
    print("\n" + "=" * 80)
    print("BASELINE RESULTS SUMMARY")
    print("=" * 80)
    correct = results["baseline"]["correct"]
    total = results["baseline"]["total"]
    percentage = (correct / total) * 100

    print(f"✅ Correct: {correct}/{total} ({percentage:.1f}%)")
    print(f"❌ Incorrect: {total - correct}/{total}")

    # Save results
    with open('baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✅ Full results saved to baseline_results.json")
    return results


if __name__ == "__main__":
    evaluate_baseline()