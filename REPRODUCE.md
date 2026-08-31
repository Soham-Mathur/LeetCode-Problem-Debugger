# Reproduction Guide: LeetCode Problem Debugger Agent

## Quick Start (5 Minutes)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd leetcode-debugger
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install anthropic python-dotenv
```

### 4. Configure API Key
Create a `.env` file in project root:
```
ANTHROPIC_API_KEY=sk-cs4-your-actual-key-here
ANTHROPIC_BASE_URL=https://api.llmsrelay.com/v1
```

Or set environment variable:
```bash
export ANTHROPIC_API_KEY="sk-cs4-your-key-here"
export ANTHROPIC_BASE_URL="https://api.llmsrelay.com/v1"
```

### 5. Run Evaluation
```bash
python evaluate_solution.py
```

Expected output: Baseline 90%, Solution 100%

---

## System Requirements

- **Python:** 3.9 or higher
- **Dependencies:** anthropic, python-dotenv
- **API:** Active Anthropic API key with sufficient credits
- **Internet:** Required for API calls
- **Disk:** ~100MB for code and test data

---

## File Structure

```
leetcode-debugger/
├── baseline.py                    # Simple prompt-based approach
├── solution.py                    # Multi-tool agent with metrics
├── code_executor.py              # Local code execution engine
├── evaluate.py                   # Baseline-only evaluation
├── evaluate_solution.py          # Full baseline vs solution comparison
├── test_cases.json               # 10 LeetCode test cases
├── .env                          # API configuration (not in repo)
├── CHANGELOG.md                  # Improvement iterations
├── REPRODUCE.md                  # This file
├── TRAJECTORIES.md               # Agent execution traces
├── trajectories.json             # Raw trajectory data (exported)
├── comparison_results.json       # Evaluation output
├── baseline_results.json         # Baseline-only results
└── README.md                     # Project overview
```

---

## Running Components

### Run Baseline Only (Quick Test)
```bash
python evaluate.py
```
**Output:** baseline_results.json
**Time:** ~1 minute
**Cost:** ~$0.03

### Run Full Evaluation (Baseline + Solution)
```bash
python evaluate_solution.py
```
**Output:** comparison_results.json
**Time:** ~3 minutes
**Cost:** ~$0.15

### Run Single Test Case
```bash
python solution.py
```
**Output:** Console output for first test case
**Time:** ~30 seconds
**Cost:** ~$0.015

### Export Agent Trajectories
```bash
python evaluate_solution.py --export-trajectories
```
**Output:** trajectories.json with complete tool traces
**Time:** ~3 minutes
**Cost:** ~$0.15

---

## Understanding Output

### Performance Metrics Table
```
Metric                  | Baseline | Solution | Delta
Accuracy               | 90.0%    | 100.0%   | +10.0%
Reasoning Depth        | 2.3/11   | 4.5/11   | +2.2
Avg Latency per Case   | 5.12s    | 34.06s   | +28.94s
Total Latency          | 51.22s   | 340.58s  | +289.36s
Estimated API Cost     | $0.027   | $0.120   | +$0.093
```

### Baseline Results
```json
{
  "baseline": {
    "correct": 9,
    "total": 10,
    "cases": [
      {
        "id": 1,
        "correct": true,
        "reasoning_depth": 3,
        "latency_sec": 5.02,
        "output": "..."
      }
    ]
  }
}
```

### Comparison Results
Contains both baseline and solution results with detailed metrics:
- accuracy scores
- reasoning depth per case
- latency measurements
- token counts
- cost calculations

See `comparison_results.json` after running evaluation for complete output.

### Trajectories
Agent execution traces showing:
- case_id and problem name
- tools executed in sequence
- intermediate outputs
- metrics (tokens, cost, latency)

See `trajectories.json` after running with --export-trajectories flag.

---

## Testing the Setup

### Minimal Test
```bash
python -c "from anthropic import Anthropic; print('Anthropic SDK installed ✓')"
```

### API Connection Test
```bash
python test_api.py
```
**Expected:** "✅ API works!"

### Test Case Verification
```bash
python code_executor.py
```
**Expected:** Test cases running, outputs showing

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install anthropic
```

### "Invalid API key" (401 Error)
Check `.env` file:
- Key should start with `sk-cs4-` (relay) or `sk-ant-` (official)
- No extra spaces or line breaks
- Base URL should include `/v1` at end: `https://api.llmsrelay.com/v1`

Test with:
```bash
python test_api.py
```

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Virtual Environment Not Activating
Make sure you're in the correct directory:
```bash
cd /path/to/leetcode-debugger
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows CMD
```

### Timeout Errors
Code execution is limited to 2 seconds per case. If you see timeouts:
- Check if code has infinite loops
- Increase timeout in code_executor.py if needed
- Some complex problems may legitimately take longer

### Rate Limiting (429 Error)
Wait a few minutes before running again. Or:
- Reduce number of test cases in evaluate_solution.py
- Run individual cases with python solution.py

---

## Exact Reproduction Steps

Follow these steps to reproduce the exact results:

### Step 1: Environment Setup
```bash
git clone <repo>
cd leetcode-debugger
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install anthropic python-dotenv
```

### Step 2: Configuration
Create `.env`:
```
ANTHROPIC_API_KEY=sk-cs4-your-key
ANTHROPIC_BASE_URL=https://api.llmsrelay.com/v1
```

### Step 3: Verify Setup
```bash
python test_api.py
# Should output: ✅ API works!
```

### Step 4: Run Baseline
```bash
python evaluate.py
# Expected: Baseline 9/10 (90%)
# Output: baseline_results.json
```

### Step 5: Run Solution
```bash
python evaluate_solution.py
# Expected: Baseline 9/10, Solution 10/10
# Output: comparison_results.json
# Time: ~3 minutes
# Cost: ~$0.15
```

### Step 6: Export Trajectories
```bash
python evaluate_solution.py --export-trajectories
# Output: trajectories.json
```

### Step 7: Verify Results
Check comparison_results.json for accuracy scores:
```
Baseline accuracy: 9/10 (90%)
Solution accuracy: 10/10 (100%)
Improvement: +10 percentage points
```

---

## Interpreting Results

### Accuracy Metrics
- **Baseline:** How well simple prompts work
- **Solution:** How well structured tools work
- **Goal:** Solution > Baseline

### Reasoning Depth
- **Scale:** 0-11 (count of reasoning keywords used)
- **Baseline:** ~2.3/11 (minimal explanation)
- **Solution:** ~4.5/11 (detailed step-by-step)
- **Improvement:** +96% more reasoning

### Latency
- **Baseline:** ~5 seconds per case
- **Solution:** ~34 seconds per case
- **Reason:** More tools = more API calls
- **Trade-off:** Speed vs Quality

### Cost
- **Per Case:** $0.003 (baseline), $0.012 (solution)
- **Per 10 Cases:** $0.03 (baseline), $0.12 (solution)
- **Total Improvement Cost:** Only +$0.09 for 100% accuracy

---

## Advanced Usage

### Run on Custom Test Cases
Edit test_cases.json:
```json
[
  {
    "id": 11,
    "problem": "Your problem here",
    "code": "def yourfunction():\n    pass",
    "test_input": "[1, 2, 3]",
    "expected_output": "6",
    "test_failure": "Expected 6, got something else"
  }
]
```

Then run:
```bash
python evaluate_solution.py
```

### Modify Tool Prompts
Edit the prompt strings in solution.py:
- `extract_constraints()` - Line ~30
- `analyze_code_patterns()` - Line ~60
- `suggest_fix()` - Line ~90

Then re-run evaluation to see impact on accuracy.

### Adjust Model or Max Tokens
In solution.py, change:
```python
model="claude-haiku-4-5-20251001",  # Change model here
max_tokens=800,                      # Adjust token limit
```

Rerun to benchmark different configurations.

### Export Detailed Metrics
The comparison_results.json file contains:
- Per-case accuracy
- Per-case reasoning depth
- Per-case latency
- Per-case cost
- Complete tool breakdown

Parse with:
```python
import json
with open('comparison_results.json') as f:
    results = json.load(f)
    print(json.dumps(results, indent=2))
```

---

## Expected Results

After successful reproduction, you should see:

```
Accuracy:
Baseline:  9/10 (90.0%)
Solution:  10/10 (100.0%)

📈 Improvement: +10.0 percentage points
📈 Multiplier: 1.11x

Reasoning Depth:
Baseline:  2.3/11
Solution:  4.5/11
📈 Reasoning improvement: +2.2 steps

Performance Benchmarks:
Metric                  | Baseline | Solution | Delta
Accuracy               | 90.0%    | 100.0%   | +10.0%
Reasoning Depth        | 2.3/11   | 4.5/11   | +2.2
Avg Latency per Case   | 5.12s    | 34.06s   | +28.94s
Total Latency          | 51.22s   | 340.58s  | +289.36s
Estimated API Cost     | $0.027   | $0.120   | +$0.093

✅ Full results saved to comparison_results.json
```

---

## Support & Issues

### Check Logs
All output is printed to console. Capture with:
```bash
python evaluate_solution.py > output.log 2>&1
```

### Verify Files Exist
```bash
ls -la baseline.py solution.py test_cases.json code_executor.py
```

### Check API Balance
Verify your API key has sufficient credits at:
- Anthropic: https://console.anthropic.com
- Relay: Your relay provider's dashboard

### Run Individual Test Case
```bash
python solution.py
# Shows detailed output for first test case
```

---

## Performance Optimization

### Reduce Test Cases
Open evaluate_solution.py and modify the evaluation loop to run only the first 5 test cases instead of all 10. This reduces latency and cost during testing.

### Disable Metrics Tracking
Comment out metrics collection in solution.py to speed up slightly (minor savings).

### Use Smaller Model
Change claude-haiku-4-5-20251001 to smaller model if available, but expect accuracy impact.

---

## Citation

If using this project, cite:

**LeetCode Problem Debugger Agent**

GitHub: [https://github.com/Soham-Mathur/LeetCode-Problem-Debugger](https://github.com/Soham-Mathur/LeetCode-Problem-Debugger)

Evaluation: 10/10 test cases, 100% accuracy

Architecture: 5-tool agent with metrics tracking

---

## Contact & Questions

For issues or questions:
1. Check this REPRODUCE.md file
2. Review CHANGELOG.md for implementation details
3. Check comparison_results.json for detailed metrics
4. Review TRAJECTORIES.md for example agent traces