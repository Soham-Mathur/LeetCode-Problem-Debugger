# LeetCode Problem Debugger Agent

An intelligent agent that debugs LeetCode solutions using structured tool use and real code execution. Achieves **100% accuracy** with **96% deeper reasoning** compared to baseline prompting.

---

## Problem Statement

Debugging LeetCode solutions manually takes **15-20 minutes per bug**. Students analyze constraints AFTER coding, not DURING debugging, leading to:
- ❌ Black-box LLM responses (no verification)
- ❌ One-shot analysis (no systematic approach)
- ❌ 90% accuracy on edge cases
- ❌ No reproducibility or explainability

**Our Solution:** Multi-tool agent with real code execution, constraint-first analysis, and transparent metrics.

---

## Results

| Metric | Baseline | Solution | Improvement |
|--------|----------|----------|-------------|
| **Accuracy** | 90.0% | **100.0%** | ✅ +10.0% |
| **Reasoning Depth** | 2.3/11 | **4.5/11** | ✅ +2.2 (+96%) |
| **Avg Latency** | 5.12s | 34.06s | Trade-off for quality |
| **Cost per Case** | $0.027 | $0.120 | Only +$0.093 |

**Test Cases:** 10 LeetCode problems (Two Sum, Contains Duplicate, Stock, etc.)

---

## Architecture

### 5-Tool Pipeline

**Tool 1: Constraint Extraction**
- Extract problem requirements automatically
- Identify input/output constraints
- Flag common bug patterns

**Tool 2: Code Pattern Analysis**
- Scan for off-by-one errors
- Check loop bounds and pointer movement
- Verify comparison operators
- Analyze state timing

**Tool 3: Real Code Execution**
- Execute buggy code with test input
- Capture actual vs expected output
- Provide concrete failure evidence

**Tool 4: Bug Identification**
- Connect constraints + patterns + execution data
- Identify exact bug location
- Explain why it violates requirements

**Tool 5: Fix Suggestion & Synthesis**
- Generate precise, testable fixes
- Verify fix with test case walk-through
- Consolidate into professional report

### Key Innovation: Constraint-First Debugging

```
Baseline (Simple):          Solution (Structured):
Code → Claude → Output      Constraints → Patterns → Execution 
(Black box)                 → Bug ID → Fix → Synthesis
                            (Transparent, Verifiable)
```

---

## Quick Start

### 1. Setup (5 minutes)

```bash
# Clone and navigate
git clone <this-repo>
cd LeetCode-Problem-Debugger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install anthropic python-dotenv
```

### 2. Configure API

Create `.env`:
```
ANTHROPIC_API_KEY=sk-cs4-your-key
ANTHROPIC_BASE_URL=https://api.llmsrelay.com/v1
```

### 3. Run Evaluation

```bash
# Baseline only (quick)
python evaluate.py

# Full comparison (complete)
python evaluate_solution.py

# Export agent traces
python evaluate_solution.py --export-trajectories
```

---

## Results Explained

### Accuracy
- **Baseline:** 9/10 (90%) - Misses edge cases
- **Solution:** 10/10 (100%) - All problems solved

### Reasoning Depth
- **Baseline:** 2.3/11 - One-line explanations
- **Solution:** 4.5/11 - Full constraint-pattern-execution verification

### Latency Trade-off
- Baseline: 5.12s (simple, fast)
- Solution: 34.06s (structured, thorough)
- **Trade-off justified:** 6.6x slower for perfect accuracy

### Cost Efficiency
- Only **$0.093 more** per problem for 100% accuracy
- **1.2 cents per problem** for all 10 cases with full metrics
- Professional-grade debugging at consumer price

---

## Files

- **baseline.py** - Simple prompt-based approach (90%)
- **solution.py** - Multi-tool agent with metrics (100%)
- **code_executor.py** - Safe local code execution
- **evaluate_solution.py** - Full evaluation pipeline
- **test_cases.json** - 10 LeetCode test problems
- **REPRODUCE.md** - Step-by-step setup guide
- **CHANGELOG.md** - Evolution from baseline to final
- **TRAJECTORIES.md** - Agent execution traces
- **comparison_results.json** - Evaluation output with metrics
- **trajectories.json** - Raw agent execution data

---

## Key Learnings

### Agents Work Best with Structure
Simple prompts achieve 90% accuracy. But systematic tool use beats one-shot reasoning every time.

### Constraint-First Design
Expert debugging follows a pattern:
1. Read requirements
2. Understand constraints
3. Trace code
4. Identify violations
5. Suggest fixes

We automated this entire workflow.

### Real Data Beats Guessing
Actual code execution data (expected vs actual output) helps agents verify their analysis, not just theorize.

### Transparency = Reproducibility
By tracking tokens, latency, and tool outputs, judges can verify and reproduce results independently.

---

## Metrics & Engineering

- ✅ **API Pricing Constants** - Haiku rates ($0.80/$4.00 per 1M tokens)
- ✅ **Token Accumulators** - All 5 tools tracked
- ✅ **Per-Tool Cost Breakdown** - See where budget goes
- ✅ **Latency Tracking** - Wall-clock time per tool
- ✅ **Error Handling** - Try-catch on every tool, graceful fallback
- ✅ **Input Validation** - Code/problem non-empty checks

---

## How to Reproduce

See **REPRODUCE.md** for:
- Exact setup steps
- Troubleshooting guide
- Custom test cases
- Advanced usage

---

## Example: Two Sum Problem

**Problem:** Find two numbers in array that sum to target

**Buggy Code (Simplified):**
The inner loop starts at index i instead of i+1, allowing the same element to pair with itself (e.g., nums[0] + nums[0] instead of nums[0] + nums[1]).

**Test Case:**
- Input: [3, 3], target = 6
- Expected: [0, 1] (two different indices)
- Buggy Output: [0, 0] (same index twice)

**Agent Analysis:**

1. **Tool 1 (Constraints):** "Must use TWO DIFFERENT indices"
2. **Tool 2 (Patterns):** "Inner loop starts at i, not i+1"
3. **Tool 3 (Execution):** Input [3,3], Expected [0,1], Got [0,0]
4. **Tool 4 (Bug ID):** "Off-by-one: loop allows same index twice"
5. **Tool 5 (Fix):** "Change range(i, ...) to range(i+1, ...)"

**Result:** ✅ Correct diagnosis with full explanation

---

## Performance Summary

**Baseline Performance:**
- 9/10 correct (90%)
- 2.3/11 reasoning depth
- 5.12s per case
- No verification

**Solution Performance:**
- 10/10 correct (100%)
- 4.5/11 reasoning depth
- 34.06s per case
- Full transparency

**Conclusion:** Perfect accuracy achieved through structured tool use and constraint-first analysis. Production-ready debugging assistance.

---

## Next Steps

- ✅ Code complete (100% accuracy on 10 problems)
- ✅ Metrics comprehensive (token/cost/latency tracking)
- ✅ Documentation complete (CHANGELOG, REPRODUCE, TRAJECTORIES)
- ⏳ Video submission (5 minutes)
- ⏳ GitHub push
- ⏳ Hackathon submission

---

## Citation

**LeetCode Problem Debugger Agent**

GitHub: https://github.com/Soham-Mathur/LeetCode-Problem-Debugger

Evaluation: 10/10 test cases, 100% accuracy

Architecture: 5-tool agent with metrics tracking and real code execution

---

## Contact

For questions or issues:
1. Review REPRODUCE.md for setup help
2. Check CHANGELOG.md for implementation details
3. See TRAJECTORIES.md for example agent runs
4. Examine comparison_results.json for detailed metrics