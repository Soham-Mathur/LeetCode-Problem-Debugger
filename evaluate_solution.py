import os
import json
from dotenv import load_dotenv
from solution import debug_code_solution
from Main import debug_code_baseline

# Load environment variables
load_dotenv()


def score_debug_output(agent_output: str, expected_bug: str) -> bool:
    """Score if agent correctly identified the bug"""
    keywords = [
        "bug", "error", "wrong", "issue", "problem",
        "off-by-one", "off by one", "index", "boundary", "condition",
        "should be", "increment", "decrement", "pointer",
        "overwriting", "overwrites", "forgot", "missing", "duplicate",
        "sum", "calculation", "loop", "return"
    ]

    output_lower = agent_output.lower()
    match_score = sum(1 for kw in keywords if kw in output_lower)

    return match_score >= 3


def evaluate_both():
    """Run baseline AND solution on all test cases"""

    # Load test cases
    with open('test_cases.json', 'r') as f:
        test_cases = json.load(f)

    results = {
        "baseline": {
            "correct": 0,
            "total": len(test_cases),
            "cases": []
        },
        "solution": {
            "correct": 0,
            "total": len(test_cases),
            "cases": []
        }
    }

    print("=" * 80)
    print("COMPARING BASELINE vs SOLUTION (Agent with Tools)")
    print("=" * 80)

    for case in test_cases:
        problem_id = case["id"]
        problem = case["problem"]
        code = case["code"]
        test_failure = case["test_failure"]
        expected_bug = case["expected_bug"]

        print(f"\n[Case {problem_id}] {problem}")
        print(f"Expected: {expected_bug}")

        # BASELINE
        try:
            baseline_output = debug_code_baseline(code, problem, test_failure)
            baseline_correct = score_debug_output(baseline_output, expected_bug)
            results["baseline"]["cases"].append({
                "id": problem_id,
                "correct": baseline_correct,
                "output": baseline_output[:200]
            })
            if baseline_correct:
                results["baseline"]["correct"] += 1
            print(f"  Baseline: {'✅' if baseline_correct else '❌'}")
        except Exception as e:
            print(f"  Baseline: ❌ ERROR")
            results["baseline"]["cases"].append({
                "id": problem_id,
                "correct": False,
                "error": str(e)[:100]
            })

        # SOLUTION
        try:
            print(f"  Solution: Running agent with tools...")
            solution_result = debug_code_solution(code, problem, test_failure)
            solution_output = solution_result["bug_analysis"]
            solution_correct = score_debug_output(solution_output, expected_bug)
            results["solution"]["cases"].append({
                "id": problem_id,
                "correct": solution_correct,
                "output": solution_output[:200]
            })
            if solution_correct:
                results["solution"]["correct"] += 1
            print(f"  Solution: {'✅' if solution_correct else '❌'}")
        except Exception as e:
            print(f"  Solution: ❌ ERROR")
            results["solution"]["cases"].append({
                "id": problem_id,
                "correct": False,
                "error": str(e)[:100]
            })

    # Print summary
    print("\n" + "=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)

    baseline_correct = results["baseline"]["correct"]
    baseline_total = results["baseline"]["total"]
    baseline_pct = (baseline_correct / baseline_total) * 100

    solution_correct = results["solution"]["correct"]
    solution_total = results["solution"]["total"]
    solution_pct = (solution_correct / solution_total) * 100

    improvement = solution_pct - baseline_pct
    improvement_multiplier = (solution_pct / baseline_pct) if baseline_pct > 0 else 0

    print(f"\nBaseline:  {baseline_correct}/{baseline_total} ({baseline_pct:.1f}%)")
    print(f"Solution:  {solution_correct}/{solution_total} ({solution_pct:.1f}%)")
    print(f"\n📈 Improvement: +{improvement:.1f} percentage points")
    print(f"📈 Multiplier: {improvement_multiplier:.2f}x")

    # Save results
    with open('comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✅ Full results saved to comparison_results.json")
    return results


if __name__ == "__main__":
    evaluate_both()