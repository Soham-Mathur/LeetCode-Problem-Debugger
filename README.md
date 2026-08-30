# 🐛 LeetCode Problem Debugger

An **AI-powered debugging system for LeetCode solutions** that analyzes incorrect code, reproduces failures locally, identifies potential bugs, and generates a suggested fix.

The project explores whether giving an AI debugger access to **execution results, code analysis, constraints, and structured debugging steps** can produce better results than simply asking an LLM to debug the code directly.

---

## 🚀 Overview

When solving LeetCode problems, an incorrect solution can fail for many different reasons:

* Incorrect conditions
* Off-by-one errors
* Wrong indexing
* Incorrect pointer movement
* Missing edge cases
* Incorrect calculations
* Runtime errors
* Infinite loops

Instead of relying on an LLM to identify the problem from the code alone, this project uses a **multi-step debugging pipeline**.

### Debugging Pipeline

```text
LeetCode Problem
       │
       ▼
  User's Code
       │
       ▼
 Test Failure Analysis
       │
       ▼
 Local Code Execution
       │
       ▼
 Constraint Analysis
       │
       ▼
 Code Pattern Analysis
       │
       ▼
 Preliminary Bug Identification
       │
       ▼
 Fix Suggestion
       │
       ▼
 Final AI Synthesis
       │
       ▼
   Debugging Report
```

The system also tracks metrics such as **token usage, latency, and estimated API cost** for the different stages.

---

## ✨ Features

### 🔍 Structured Bug Analysis

Instead of immediately asking an LLM for the answer, the system breaks debugging into multiple stages:

1. Analyze the problem constraints
2. Analyze code patterns
3. Execute the submitted code
4. Identify the likely bug
5. Suggest a fix
6. Synthesize the final debugging explanation

### ⚡ Local Code Execution

The debugger can execute Python solutions against extracted test inputs and compare the actual output with the expected output.

Execution includes basic guardrails such as:

* Subprocess isolation
* Execution timeout
* Runtime error detection
* Output truncation
* Expected vs. actual output comparison

The current executor uses a **2-second execution limit** to detect cases such as infinite loops.

### 🤖 AI-Powered Debugging

The project uses the **Anthropic API** to perform different reasoning stages, including bug identification, fix generation, and final analysis.

The final analysis is instructed to:

* Clearly explain the bug
* Explain why the logic is incorrect
* Confirm why the fix works
* Show the relevant corrected code

### 📊 Baseline Comparison

The project includes a simple baseline approach that sends the code, problem, and test failure directly to an LLM.

This can then be compared against the structured debugging agent.

```text
             ┌─────────────────┐
             │   Test Case     │
             └────────┬────────┘
                      │
             ┌────────▼────────┐
             │    Baseline     │
             │  Direct LLM     │
             └────────┬────────┘
                      │
                      ▼
                Debug Output


             ┌─────────────────┐
             │   Test Case     │
             └────────┬────────┘
                      │
             ┌────────▼────────┐
             │ Structured Agent│
             ├─────────────────┤
             │ Execution       │
             │ Constraints     │
             │ Patterns        │
             │ Bug Analysis    │
             │ Fix Suggestion  │
             │ Synthesis       │
             └────────┬────────┘
                      │
                      ▼
                Debug Output
```

### 📈 Evaluation Metrics

The evaluation framework records:

* Debugging correctness
* Reasoning depth
* Input tokens
* Output tokens
* Total tokens
* Latency
* Estimated API cost

Results can be used to compare the baseline and structured approaches across the same test cases.

---

## 🗂️ Project Structure

```text
LeetCode-Problem-Debugger/
│
├── solution.py
│   └── Main structured AI debugging agent
│
├── code_executor.py
│   └── Executes submitted Python code against test inputs
│
├── evaluate.py
│   └── Evaluates the baseline debugger
│
├── evaluate_solution.py
│   └── Compares baseline vs. structured debugger
│
├── analyze_failure.py
│   └── Analyzes comparison results and identifies failure cases
│
├── test_cases.json
│   └── Benchmark problems, incorrect solutions and expected bugs
│
├── test.py
│   └── Basic Anthropic API connectivity test
│
├── test_api.py
│   └── API-related testing
│
├── test_key.py
│   └── API key testing
│
├── TRAJECTORIES.md
│   └── Debugging trajectories / experiment notes
│
├── REPRODUCE.md
│   └── Reproduction instructions
│
├── CHANGELOG.md
│   └── Project changes
│
└── .gitignore
```

---

## 🛠️ Tech Stack

* **Python**
* **Anthropic API**
* **Claude**
* **Subprocess-based code execution**
* **JSON**
* **python-dotenv**

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Soham-Mathur/LeetCode-Problem-Debugger.git
cd LeetCode-Problem-Debugger
```

### 2. Install dependencies

```bash
pip install anthropic python-dotenv
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

If you're using a custom Anthropic-compatible endpoint:

```env
ANTHROPIC_BASE_URL=your_base_url
```

> **Never commit your API key to GitHub.**

---

## ▶️ Running the Debugger

Run the main debugging system:

```bash
python solution.py
```

Run the baseline evaluation:

```bash
python evaluate.py
```

Run the baseline vs. structured-agent comparison:

```bash
python evaluate_solution.py
```

Run the code executor independently:

```bash
python code_executor.py
```

---

## 🧪 Evaluation

The project includes a collection of intentionally incorrect LeetCode solutions together with their corresponding test failures and expected bug descriptions.

The evaluation system runs both:

**Baseline**

```text
Code + Problem + Failure
          ↓
        LLM
          ↓
     Debug Output
```

and:

**Structured Agent**

```text
Code + Problem + Failure
          ↓
   ┌───────────────┐
   │ Code Analysis │
   │ Constraints   │
   │ Execution     │
   │ Bug Detection │
   │ Fix Suggestion│
   │ Synthesis     │
   └───────────────┘
          ↓
     Debug Output
```

The results are saved for further analysis, allowing the approaches to be compared on the same benchmark.

---

## 🎯 Motivation

Large language models can often identify bugs in programming solutions, but simply providing code and asking *"What's wrong?"* does not necessarily produce reliable debugging.

This project explores a different approach:

> **Give the model evidence before asking it to reason about the bug.**

By combining deterministic tools such as code execution with LLM-based reasoning, the goal is to make debugging more **evidence-driven, explainable, and measurable**.

---

## 🔬 Current Limitations

This is an experimental project and has several limitations:

* Currently focused primarily on **Python** solutions.
* Code execution is intended for controlled debugging experiments and should not be considered a fully secure sandbox.
* Bug correctness is currently evaluated using heuristic keyword-based scoring.
* The benchmark is relatively small.
* LLM outputs are inherently non-deterministic.
* API latency and cost depend on the selected model and request.

---

## 🔮 Future Improvements

Potential future improvements include:

* [ ] Secure sandboxed execution
* [ ] Support for Java, C++, JavaScript and other LeetCode languages
* [ ] Larger and more diverse benchmark
* [ ] AST-based static code analysis
* [ ] Better bug classification
* [ ] Semantic evaluation instead of keyword-based scoring
* [ ] Automatic generation of additional test cases
* [ ] Iterative debugging loops
* [ ] Automatic patch generation and verification
* [ ] Web interface for submitting code
* [ ] Detailed experiment dashboards
* [ ] More rigorous accuracy/cost/latency evaluation

---

## 📚 Research Direction

The project can be viewed as an experiment in **tool-augmented LLM reasoning for software debugging**.

The central question is:

> **Does giving an LLM access to execution evidence and structured intermediate analysis improve its ability to debug incorrect algorithmic solutions?**

The repository contains the evaluation and reproduction files needed to experiment with this question.

---

## 📄 License

This project is intended for educational and experimental purposes.

---

## 👨‍💻 Author

**Soham Mathur**

GitHub: [@Soham-Mathur](https://github.com/Soham-Mathur)

---

⭐ If you find the project interesting, feel free to star the repository and experiment with the debugging pipeline.
