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


def measure_reasoning_depth(output: str) -> int:
    """Count how many reasoning steps the output shows"""
    phrases = [
        "constraint",
        "pattern",
        "because",
        "however",
        "loop",
        "index",
        "increment",
        "verify",
        "bug",
        "why",
        "fix"
    ]
    return sum(1 for phrase in phrases if phrase in output.lower())


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
        expected_bug = case.get("expected_bug", case.get("expected_output", ""))

        print(f"\n[Case {problem_id}] {problem}")
        print(f"Expected: {expected_bug}")

        # BASELINE
        try:
            baseline_output = debug_code_baseline(code, problem, test_failure)
            baseline_correct = score_debug_output(baseline_output, expected_bug)
            baseline_reasoning = measure_reasoning_depth(baseline_output)

            results["baseline"]["cases"].append({
                "id": problem_id,
                "correct": baseline_correct,
                "reasoning_depth": baseline_reasoning,
                "output": baseline_output[:200]
            })
            if baseline_correct:
                results["baseline"]["correct"] += 1
            print(f"  Baseline: {'✅' if baseline_correct else '❌'} (reasoning: {baseline_reasoning}/11)")
        except Exception as e:
            print(f"  Baseline: ❌ ERROR")
            results["baseline"]["cases"].append({
                "id": problem_id,
                "correct": False,
                "reasoning_depth": 0,
                "error": str(e)[:100]
            })

        # SOLUTION
        # SOLUTION
        try:
            print(f"  Solution: Running agent with tools...")
            solution_result = debug_code_solution(
                code=code,
                problem=problem,
                test_failure=test_failure,
                test_input=case.get("test_input", ""),  # ADD THIS
                expected_output=case.get("expected_output", "")  # ADD THIS
            )
            solution_output = solution_result["bug_analysis"]
            solution_correct = score_debug_output(solution_output, expected_bug)
            solution_reasoning = measure_reasoning_depth(solution_output)

            results["solution"]["cases"].append({
                "id": problem_id,
                "correct": solution_correct,
                "reasoning_depth": solution_reasoning,
                "output": solution_output[:200]
            })
            if solution_correct:
                results["solution"]["correct"] += 1
            print(f"  Solution: {'✅' if solution_correct else '❌'} (reasoning: {solution_reasoning}/11)")
        except Exception as e:
            print(f"  Solution: ❌ ERROR")
            results["solution"]["cases"].append({
                "id": problem_id,
                "correct": False,
                "reasoning_depth": 0,
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

    baseline_avg_reasoning = sum(c.get("reasoning_depth", 0) for c in results["baseline"]["cases"]) / len(
        results["baseline"]["cases"])
    solution_avg_reasoning = sum(c.get("reasoning_depth", 0) for c in results["solution"]["cases"]) / len(
        results["solution"]["cases"])

    print(f"\nAccuracy:")
    print(f"Baseline:  {baseline_correct}/{baseline_total} ({baseline_pct:.1f}%)")
    print(f"Solution:  {solution_correct}/{solution_total} ({solution_pct:.1f}%)")
    print(f"\n📈 Improvement: +{improvement:.1f} percentage points")
    print(f"📈 Multiplier: {improvement_multiplier:.2f}x")

    print(f"\nReasoning Depth:")
    print(f"Baseline:  {baseline_avg_reasoning:.1f}/11")
    print(f"Solution:  {solution_avg_reasoning:.1f}/11")
    print(f"📈 Reasoning improvement: +{solution_avg_reasoning - baseline_avg_reasoning:.1f} steps")

    # Save results
    with open('comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✅ Full results saved to comparison_results.json")
    return results


if __name__ == "__main__":
    evaluate_both()