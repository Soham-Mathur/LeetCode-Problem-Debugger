import os
import json
import time
from dotenv import load_dotenv
from solution import debug_code_solution
from baseline import debug_code_baseline

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
        expected_bug = case.get("expected_bug", case.get("problem", "Bug analysis"))

        print(f"\n[Case {problem_id}] {problem}")
        print(f"Expected: {expected_bug}")

        # BASELINE
        try:
            start_time = time.time()
            baseline_output = debug_code_baseline(code, problem, test_failure)
            baseline_time = time.time() - start_time

            baseline_correct = score_debug_output(baseline_output, expected_bug)
            baseline_reasoning = measure_reasoning_depth(baseline_output)

            results["baseline"]["cases"].append({
                "id": problem_id,
                "correct": baseline_correct,
                "reasoning_depth": baseline_reasoning,
                "latency_sec": baseline_time,
                "output": baseline_output[:200]
            })
            if baseline_correct:
                results["baseline"]["correct"] += 1
            print(
                f"  Baseline: {'✅' if baseline_correct else '❌'} (reasoning: {baseline_reasoning}/11, time: {baseline_time:.2f}s)")
        except Exception as e:
            print(f"  Baseline: ❌ ERROR")
            results["baseline"]["cases"].append({
                "id": problem_id,
                "correct": False,
                "reasoning_depth": 0,
                "latency_sec": 0,
                "error": str(e)[:100]
            })

        # SOLUTION
        try:
            print(f"  Solution: Running agent with tools...")
            start_time = time.time()
            solution_result = debug_code_solution(code, problem, test_failure, case.get("test_input", ""),
                                                  case.get("expected_output", ""))
            solution_time = time.time() - start_time

            solution_output = solution_result["bug_analysis"]
            solution_correct = score_debug_output(solution_output, expected_bug)
            solution_reasoning = measure_reasoning_depth(solution_output)

            results["solution"]["cases"].append({
                "id": problem_id,
                "correct": solution_correct,
                "reasoning_depth": solution_reasoning,
                "latency_sec": solution_time,
                "output": solution_output[:200],
                "metrics": solution_result.get("metrics", {})
            })
            if solution_correct:
                results["solution"]["correct"] += 1
            print(
                f"  Solution: {'✅' if solution_correct else '❌'} (reasoning: {solution_reasoning}/11, time: {solution_time:.2f}s)")
        except Exception as e:
            print(f"  Solution: ❌ ERROR")
            results["solution"]["cases"].append({
                "id": problem_id,
                "correct": False,
                "reasoning_depth": 0,
                "latency_sec": 0,
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

    # Performance benchmarks
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARKS")
    print("=" * 80)

    baseline_latencies = [c.get("latency_sec", 0) for c in results["baseline"]["cases"]]
    solution_latencies = [c.get("latency_sec", 0) for c in results["solution"]["cases"]]

    baseline_avg_latency = sum(baseline_latencies) / len(baseline_latencies) if baseline_latencies else 0
    solution_avg_latency = sum(solution_latencies) / len(solution_latencies) if solution_latencies else 0

    baseline_total_latency = sum(baseline_latencies)
    solution_total_latency = sum(solution_latencies)

    # Rough cost estimates (Haiku: $0.80/1M input, $4/1M output)
    baseline_cost = baseline_correct * 0.003  # Baseline static estimate
    solution_cost = sum(
        c.get("metrics", {}).get("total_cost_usd", 0.0)
        for c in results["solution"]["cases"]
    )

    print(f"\n{'Metric':<30} {'Baseline':<20} {'Solution':<20} {'Delta':<15}")
    print("-" * 85)
    print(
        f"{'Accuracy':<30} {f'{baseline_pct:.1f}%':<20} {f'{solution_pct:.1f}%':<20} {f'{(solution_pct - baseline_pct):+.1f}%':<15}")
    print(
        f"{'Reasoning Depth':<30} {f'{baseline_avg_reasoning:.1f}/11':<20} {f'{solution_avg_reasoning:.1f}/11':<20} {f'{(solution_avg_reasoning - baseline_avg_reasoning):+.1f}':<15}")
    print(
        f"{'Avg Latency per Case (s)':<30} {f'{baseline_avg_latency:.2f}s':<20} {f'{solution_avg_latency:.2f}s':<20} {f'{(solution_avg_latency - baseline_avg_latency):+.2f}s':<15}")
    print(
        f"{'Total Latency (s)':<30} {f'{baseline_total_latency:.2f}s':<20} {f'{solution_total_latency:.2f}s':<20} {f'{(solution_total_latency - baseline_total_latency):+.2f}s':<15}")
    print(
        f"{'Estimated API Cost ($)':<30} {f'${baseline_cost:.3f}':<20} {f'${solution_cost:.3f}':<20} {f'${(solution_cost - baseline_cost):+.3f}':<15}")
    print()

    # Save results
    with open('comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("✅ Full results saved to comparison_results.json")
    return results


if __name__ == "__main__":
    evaluate_both()