# Task Contract Standard

Every implementation task must include:

| Field | Required | Purpose |
|---|---|---|
| `task_id` | Yes | Stable identifier |
| `title` | Yes | Short outcome |
| `owner` | Yes | One accountable agent |
| `objective` | Yes | Desired result |
| `inputs` | Yes | Source artifacts |
| `scope` | Yes | Included work |
| `out_of_scope` | Yes | Explicit exclusions |
| `dependencies` | Yes | Prerequisite task IDs |
| `owned_paths` | Yes | Files/resources the owner may change |
| `acceptance_criteria` | Yes | Observable pass conditions |
| `verification` | Yes | Commands/checks/evidence |
| `status` | Yes | Current execution state |

A task may be marked completed only when `completion_evidence` is populated.
