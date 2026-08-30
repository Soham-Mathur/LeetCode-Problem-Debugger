# Replication Guide

Follow these steps to reproduce the agent evaluation benchmark and verify the results.

## Prerequisites
- Python 3.9+
- Anthropic API Key

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Soham-Mathur/LeetCode-Problem-Debugger
```


2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the project root and add your API key:
   ```env
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Running the Evaluation

To execute the full benchmark comparing the baseline model against the multi-tool solution agent:

```bash
python evaluate_solution.py --export-trajectories
```

### Expected Output Artifacts
Upon completion, the script will print a comparison table to the terminal and generate the following files:
*   `comparison_results.json`: Raw telemetry, token usage, cost, and latency data per test case.
*   `TRAJECTORIES.json`: Detailed step-by-step tool execution traces.