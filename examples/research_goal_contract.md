# Goal Contract

## 1. Outcome
Produce the strongest evidence-backed reproduction or audit of the requested research claims using the available materials and local resources.

## 2. Business / User Value
Reduce uncertainty by separating confirmed evidence, approximate reconstruction, blocked claims, and remaining unknowns.

## 3. Verification Surface
- claim inventory mapped to available evidence
- final audit report separating confirmed, approximate, proxy-supported, blocked, and uncertain claims

## 4. Constraints
- Do not overstate unsupported claims; label proxy evidence and blocked claims honestly.

## 5. Boundaries
### In Scope
- provided paper/materials
- available datasets/code
- local reproducible experiments
- final audit report

### Out of Scope / Non-Goals
- unrelated rewrites
- large architectural changes not required by the Goal
- speculative work without evidence

## 6. Required Context
- source paper or research materials
- available code/data/checkpoints
- local environment constraints

## 7. Assumptions
- The current repository or provided materials contain enough context to inspect and validate the task.
- If a required command, dataset, credential, or environment is unavailable, the agent will report the blocker instead of fabricating success.

## 8. Acceptance Criteria
- A claim inventory maps each major claim to evidence status.
- Final report separates exact reproduction, approximate reconstruction, proxy support, blocked claims, and uncertainty.

## 9. Iteration Policy
- After each attempt, record what was inspected or changed.
- Record the evidence observed from tests, benchmarks, logs, artifacts, source material, or review checklist.
- Compare the latest evidence against the acceptance criteria before deciding whether to continue.
- Choose the next lowest-risk action that most directly improves evidence toward completion.
- Do not continue if the next action would exceed scope, budget, or available evidence.

## 10. Checkpoints
- Inventory the target claims and required evidence.
- Map available materials, code, data, and local constraints.
- Attempt feasible reproductions or reconstructions.
- Label unsupported or blocked claims with missing inputs.
- Produce final audit with confidence levels and remaining uncertainty.

## 11. Failure Recovery
- If validation fails, isolate or revert the latest change and preserve the failing evidence.
- If the verification surface cannot run, report the command, error, missing input, and what would unlock progress.
- If progress stalls, summarize attempted paths and switch only to a lower-risk path supported by evidence.

## 12. Blocked Stop Condition
Stop when the required verification surface cannot be accessed, no valid path remains within the stated boundaries, or further progress would require guessing. Report attempted paths, evidence gathered, blocker, and next input needed.

## 13. Budget / Runtime Limit
Default to five bounded iterations or ask the user before continuing beyond the available evidence/budget.

## 14. Deliverables
- claim inventory
- reproducibility artifacts where feasible
- evidence-backed audit report

## 15. Risk Level
Medium

## 16. Estimated Runtime
Long

## 17. Goal Quality Score
- clarity: 9.0/10
- verifiability: 9.5/10
- scope_control: 8.0/10
- autonomy_readiness: 9.0/10
- drift_risk: Low
- overall: 8.9/10

