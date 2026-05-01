# Agent Instructions for Logic Lab

## Commit Policy

**Do NOT commit changes to git.**

The user will handle all git commits manually. After implementing features or fixes:
- Write/edit code files as needed
- Create new directories and files
- Run syntax checks and basic tests
- But DO NOT run `git add` or `git commit`

Instead, leave the working directory in a state ready for the user to commit. The user will review changes and commit when appropriate.

## Implementation Preferences

- Implement features directly without asking for confirmation on straightforward tasks
- For multi-step or architectural decisions, use EnterPlanMode to get user alignment first
- Run syntax verification on Python files to catch errors early
- Test code when possible before completing the task
- Use concise communication - state what was done and what's next

## Project Context

This project translates JavaScript examples from "The Nature of Code" (noc-book-2) into Python using py5:

- Each simulation gets its own `/simulation/{name}/` directory
- Standard structure: `{name}.py` (main file), `README.md` (instructions), `/screenshots/` (for outputs)
- Target: Full translation of Chapter 2, 5, 6, 8, and 9 examples
