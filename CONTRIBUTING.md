# Contributing

## Principles

- Keep each specialist's mission narrow and non-overlapping.
- Prefer a shared skill over copying the same procedure into multiple agents.
- Keep skill instructions portable; isolate platform-specific syntax in adapters.
- Every new task workflow must define inputs, outputs, ownership, and verification.
- Never describe an operation as completed unless it was actually executed and verified.

## Adding an agent

1. Create `modules/<module-id>/agents/<agent-id>.md` in the appropriate source module (or add a new module with `module.json`).
2. Define mission, responsibilities, boundaries, inputs, outputs, handoff, and quality gates.
3. Keep agent frontmatter free of external plugin dependencies; all ecosystem capabilities are bundled into the single `ai-agent` plugin.
4. Add or update an evaluation scenario.
5. Run `python scripts/build_single_plugin.py`.
6. Run `python scripts/validate_repo.py`, `python scripts/validate_plugin.py`, and `python scripts/build_single_plugin.py --check`.
7. If Antigravity CLI is installed, run `agy plugin validate --strict .`.

## Adding a skill

1. Create `modules/core-engineering-skills/skills/<skill-id>/SKILL.md` or place the skill in the most relevant source module.
2. Use valid Agent Skills YAML frontmatter (`name`, `description`).
3. Include trigger conditions, procedure, output contract, verification, and failure modes.
4. Test the skill against at least one positive and one negative scenario.
5. Rebuild and validate the root bundle.

## Releasing

The only installable distribution target is this repository: `https://github.com/hd159/ai-agent`.

1. Run the build and validation commands above.
2. Commit the canonical source and generated root bundle together.
3. Push to the `main` branch.
4. Verify GitHub Actions passes.
5. Verify installation with `agy plugin install https://github.com/hd159/ai-agent`.

Do not create per-agent GitHub repositories or publish nested `modules/<id>` directories as independent repositories.
