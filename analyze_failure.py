import json

with open('comparison_results.json', 'r') as f:
    results = json.load(f)

print("Cases where BASELINE was correct but SOLUTION was wrong:\n")
for baseline_case, solution_case in zip(results["baseline"]["cases"], results["solution"]["cases"]):
    if baseline_case["correct"] and not solution_case["correct"]:
        print(f"Case {baseline_case['id']} FAILED")
        print(f"Baseline output: {baseline_case['output']}")
        print(f"Solution output: {solution_case['output']}\n")