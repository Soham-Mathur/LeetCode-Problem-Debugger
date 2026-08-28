# Improvement Changelog: LeetCode Problem Debugger

## Executive Summary
Baseline (simple prompt) and solution (agent with tools) both achieve excellent accuracy on 10 diverse LeetCode problems. The solution trades minimal accuracy for **structured reasoning transparency**.

---

## Baseline: Simple Prompt Approach

**Implementation:**
```python
def debug_code_baseline(code, problem, test_failure):
    message = client.messages.create(
        model="claude-sonnet-4.6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"Debug this:\n\nPROBLEM: {problem}\n\nCODE:\n{code}\n\nTEST FAILURE: {test_failure}\n\nWhat is the bug?"
        }]
    )
    return message.content[0].text
```

**Results:** 10/10 correct (100%)

**Strengths:**
- Simple and fast (~5 sec per case)
- Claude's base ability is excellent
- No engineering overhead

**Weaknesses:**
- No structured reasoning shown
- Single-pass analysis (no verification)
- Harder to explain WHY it's a bug to students
- Would struggle on more complex problems

---

## Iteration 1: Add Constraint Extraction Tool

**Rationale:** Many bugs violate problem constraints. By extracting constraints first, the agent can verify if code satisfies requirements.

**Change:**
```python
def extract_constraints(problem: str) -> str:
    """Extract key constraints before analyzing code"""
    message = client.messages.create(
        model="claude-sonnet-4.6",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Extract constraints from: {problem}
            
List:
1. Input constraints (size, range)
2. Output requirements
3. Special conditions (in-place, no duplicates, etc.)"""
        }]
    )
    return message.content[0].text
```

**Usage in Solution:**
1. Extract constraints from problem
2. Analyze code patterns
3. Synthesize bug analysis with constraints as verification framework

**Results:** 9-10/10 correct (~90-100%)

**Evidence:**
- **Case 1 (Two Sum):** Agent verifies "must use TWO DIFFERENT numbers" constraint, catches off-by-one
- **Case 4 (Stock):** Agent identifies "must track MINIMUM price" constraint, catches max() bug
- **Case 5 (Duplicates):** Agent verifies set-based logic against constraint

**Example from Case 4:**

Input code:
```python
min_price = max(min_price, prices[i])  # BUG: should be min()
```

Baseline output: