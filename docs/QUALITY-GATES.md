# v0.3 Quality Gates — reusable project verification

This is a **generic** validation layer for applications that use the AI Agent Ecosystem. Product-specific implementation, tests, audit findings, and approval records stay in the product repository.

## What is enforced?

- JSON Schema validation for \`team.json\`, \`plan.json\`, \`state.json\`, every \`tasks/*.json\`, JSON handoffs, and the independent task verification report.
- Unique task IDs, dependency existence, dependency cycle detection, and task/state status and owner agreement.
- Every \`completed\` task has an independent QA report with results for **all** its acceptance criteria.
- Passing checks have non-empty evidence files; executable checks specify a real command and exit code 0.
- The report references a full Git commit and fails if application/tests changed since that commit, including dirty files.
- The independent reviewer differs from the task owner and, when a QA team role is configured, is that QA specialist.
- Production release requires every task completed, no blockers/decisions, and all mandatory approvals (including \`production_deployment\`) marked approved with approver and timestamp.

## Install the CLI dependencies

\`\`\`powershell
cd C:\work\ai-agent
python -m pip install -r requirements-dev.txt
\`\`\`

The plugin itself remains installable with \`agy plugin install https://github.com/hd159/ai-agent\`. The validation scripts live in a clone of the generic repo; plugin installation does not clone scripts into your application's workspace.

## Commands

\`\`\`powershell
# Validate the current product's project memory and all completed tasks
python .\scripts\quality_gate.py validate --project "C:\work\my-product"

# Before marking an implementation task completed, QA runs
python .\scripts\quality_gate.py task --project "C:\work\my-product" --task-id BE-001

# Before recommending any production release
python .\scripts\quality_gate.py release --project "C:\work\my-product"
\`\`\`

All commands are read-only and exit 0 on success, 1 on invalid artifacts, 2 if dependencies/arguments are missing.

## Evidence layout in each project

\`\`\`text
my-product/
└── .agent-ecosystem/
    └── execution/
        ├── state.json
        ├── plan.json
        ├── tasks/BE-001.json
        ├── handoffs/
        └── verification/
            ├── VERIFICATION_TEMPLATE.json
            ├── BE-001.json
            └── evidence/
                └── be-001-test.log
\`\`\`

Each task verification record is validated against [verification.schema.json](../contracts/schemas/verification.schema.json). The \`criterion\` strings must match the task acceptance criteria exactly. Each passed criterion references one or more passing check IDs.

The \`source_commit\` field must be a 40-digit lowercase Git SHA. A verification artifact may be committed later as long as only \`.agent-ecosystem/\` changes; modifications to app code, tests, configuration, or other non-memory files invalidate previously recorded evidence. No source changes may remain uncommitted when completing a task. Save only sanitized logs: no access tokens, database credentials, secrets, or user data.

## Correct lifecycle

1. Implementation agent delivers code on a branch, with tests, and commits the source.
2. QA reviews independently and executes relevant checks on that committed revision.
3. QA saves sanitized output logs and \`verification/TASK-ID.json\` with the commit and criterion-level evidence.
4. Orchestrator sets task to \`in_review\` and runs \`quality_gate.py task\`.
5. On success, Orchestrator sets task and state statuses to \`completed\` and runs \`quality_gate.py validate\`.
6. On failure, task stays \`in_review\`/\`blocked\`; missing checks and blockers are explicit.
7. For a release, protected CI independently runs relevant tests and the release gate. The human explicitly approves production deployment.

## Backward compatibility / existing projects

Existing projects may have noncanonical fields such as \`depends_on\` instead of \`dependencies\` or free-form completion evidence. The new validator **intentionally fails closed** on such data. Preserve backups and history, then migrate old task/state/handoff records into the canonical schemas; do not reinterpret or silently mark legacy tasks completed.

The bootstrap script remains non-destructive: it refuses to overwrite a non-empty \`.agent-ecosystem/\`. For existing projects, create the \`execution/verification/evidence/\` directory and records only as needed.

## Trust boundaries and limitations

- A passed gate validates artifact schema, cross-file consistency, reported exit codes, file existence, and Git freshness.
- **It does not execute the listed tests**, cryptographically attest that the tests ran, authenticate the QA identity, verify the authenticity of a reported human approval, or replace code review.
- An agent that can edit code and QA reports can fabricate logs or approval fields. Use GitHub branch protection, required external CI, CODEOWNERS, mandatory human reviewers, and deployment environment approvals for enforceable production controls.
- A Git SHA alone does not prove that a system under test matches staging/production. Keep environment identity and integration test coverage in the QA record.
- The generic gate does not inspect the business semantics of API payloads, database migrations, payments, or domain policies. Those require product-specific tests and the next architecture/contract-drift phase.
