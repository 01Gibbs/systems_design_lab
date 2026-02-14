# Branch Naming Standards & Traceability

To ensure every change is traceable to roadmap work, use the following branch naming convention:

## Branch Naming Convention

- **Feature branches:** `feature/{roadmap-id}-{short-description}`
- **Bugfix branches:** `fix/{roadmap-id}-{short-description}`
- **Docs branches:** `docs/{roadmap-id}-{short-description}`
- **Chore/infra branches:** `chore/{roadmap-id}-{short-description}`

Where `{roadmap-id}` is the unique scenario, epic, or phase identifier from `ROADMAP.md` or `SCENARIO_TRACKER.md` (e.g., `phase-4b`, `scenario-17`, `docs-obs-stack`).

### Examples

- `feature/phase-4b-cache-metrics`
- `fix/scenario-17-deadlock`
- `docs/phase-5-tutorials`
- `chore/phase-4-standards`

## Traceability Requirements

- Always reference the roadmap or scenario ID in the PR title and commit messages.
- Link PRs to the relevant section in `ROADMAP.md` or `SCENARIO_TRACKER.md`.
- Each branch and change must map directly to a tracked work item.

## Workflow Update

1. **Before starting work:**
   - Identify the relevant roadmap/scenario ID.
   - Create a branch using the convention above.
2. **During development:**
   - Reference the roadmap/scenario ID in all commit messages.
   - Keep commits atomic and descriptive.
3. **On PR:**
   - Link to the roadmap/scenario in the PR description.
   - Ensure branch name and PR title match the convention.

---

_This standard is mandatory for all new work. It ensures full traceability and auditability as the project roadmap advances._
