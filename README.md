# A2A-MCP

Small `uv`-based setup notes for the notebook workflows in this repo.

## Setup

1. Create the environment and install dependencies:

   ```powershell
   uv sync
   ```

2. Add a `.env` file with at least one of these keys:

   ```env
   GOOGLE_API_KEY=...
   ```

   or

   ```env
   GEMINI_API_KEY=...
   ```

## Workflows

- Policy agent server (Lesson 4):

  ```powershell
  uv run a2a_policy_agent.py
  ```

- A2A client flow (Lesson 5):
  Keep the policy agent running, then open `L5.ipynb` in your notebook editor and run the cells.

- Research agent server (Lesson 6):
  First generate `a2a_research_agent.py` from `L6.ipynb`, then run:

  ```powershell
  uv run a2a_research_agent.py
  ```

- Multi-agent workflows (Lessons 7-8):
  Keep the required agent servers running, then execute `L7.ipynb` or `L8.ipynb`.

## Test

Run the small automated test suite with:

```powershell
uv run python -m unittest discover -s tests -v
```
