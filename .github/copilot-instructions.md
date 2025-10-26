# AI Coding Assistant Instructions

This file gives the immediate, discoverable context an AI coding assistant needs to be productive in this repository.

## Quick safety rule (must-read)
- For development and testing in this repo, run only the two entry-point scripts: `api_server.py` and `file-directory.py`.
- Do not run other project files directly unless asked and granted context about side effects.

Example (run from project root):

```bash
# from zsh / macOS
python api_server.py
python file-directory.py
```

## Why this restriction
- The project is early-stage and contains files that may expect environment variables, external APIs, or incomplete implementations. Restricting execution reduces accidental API calls, leaked secrets, or partially-implemented behavior.

## Short project overview (discoverable facts)
- Language: Python (single-module prototype)
- Key files:
  - `model_generation.py` — placeholder module for audio model generation using external APIs.
  - `api_server.py` — (entry point) runs the API server for the voice/model endpoints.
  - `file-directory.py` — (entry point) utility that performs local file/directory operations used during development.
  - `.env` — contains API credentials used by the code (use `os.getenv()` to read).

## Environment & running
- Credentials are expected in environment variables. The repo contains `.env` for local convenience; prefer `os.getenv()` in code and load `.env` in local dev only.
- If you need to run either allowed script and it requires environment variables, set them in your shell (don't commit secrets).

## What to change in this file
- Keep this file up-to-date when new safe entry points are added. If you add a script intended to be run directly, add it to the "Quick safety rule" list and provide a one-line justification.

## Notes for AI assistants
- Prefer reading `api_server.py` and `file-directory.py` before suggesting runtime changes. Use `model_generation.py` only to implement logic when asked; do not execute it by itself.
- When adding examples, include exact paths and commands (zsh) and note environment variables required.

---
If anything in these instructions is unclear or you want the run-safety rule relaxed/expanded, tell me which files to review and I'll update this guidance.