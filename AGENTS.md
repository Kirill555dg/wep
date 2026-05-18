# Development Rules

## General Principles
- Think before coding. Read existing files first.
- Prefer editing over rewriting entire files.
- Skip files >100KB unless required.
- Test code before completion.
- Keep solutions simple and direct.
- User instructions override all rules.

## Output Format
- Code first, explanation only if non-obvious.
- Minimal comments - only for unclear logic.
- No boilerplate unless requested.

## Code Rules
- Simplest working solution. No over-engineering.
- No abstractions for single-use operations.
- Read files before modifying. Never edit blind.
- No docstrings/type annotations on unchanged code.
- No error handling for impossible scenarios.
- Three similar lines > premature abstraction.
- Define all constants as variables, never use magic values/literals.

## Code Review
- State bug, show fix, stop.
- No scope creep or compliments.

## Debugging
- Never speculate without reading code first.
- State findings, location, and fix in one pass.
- If cause unclear: say so, don't guess.

## Tooling

- **Backend**: uv (Python 3.12+)
- **Frontend**: bun (Node.js runner)
- **Database**: PostgreSQL + Alembic migrations

When working with Python: `uv run <command>`
When working with Node.js packages: `bun <command>`

## Formatting
- Plain text only: hyphens, straight quotes.
- No decorative symbols.
- Copy-paste safe code output.
