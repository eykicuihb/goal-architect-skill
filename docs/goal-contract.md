# Goal Contract

## 1. Outcome
Achieve the requested performance target (p95 latency is below 120ms) for the relevant system while preserving correctness.

## 2. Business / User Value
Improve user experience and operational efficiency without sacrificing correctness.

## 3. Verification Surface
- benchmark output showing the target metric is met
- explicit acceptance checklist
- final evidence-backed report

## 4. Constraints
- Do not regress correctness tests.
- Do not regress correctness tests or public behavior.

## 5. Boundaries
### In Scope
- current repository
- relevant service/module
- benchmark fixtures
- related tests

### Out of Scope / Non-Goals
- unrelated rewrites
- large architectural changes not required by the Goal
- speculative work without evidence
- changes outside the relevant module unless evidence shows they are necessary

## 6. Required Context
- benchmark command and baseline result
- correctness test command

## 7. Assumptions
- The current repository or provided materials contain enough context to inspect and validate the task.
- If a required command, dataset, credential, or environment is unavailable, the agent will report the blocker instead of fabricating success.

## 8. Acceptance Criteria
- Target metric is met: p95 latency is below 120ms.
- Benchmark output demonstrates the performance target is met on the agreed benchmark.
- Correctness test suite remains green.

## 9. Iteration Policy
- After each attempt, record what was inspected or changed.
- Record the evidence observed from tests, benchmarks, logs, artifacts, source material, or review checklist.
- Compare the latest evidence against the acceptance criteria before deciding whether to continue.
- Choose the next lowest-risk action that most directly improves evidence toward completion.
- Do not continue if the next action would exceed scope, budget, or available evidence.

## 10. Checkpoints
- Establish baseline/current state and capture evidence.
- Identify the smallest high-confidence next action.
- Apply or propose one bounded intervention.
- Run the verification surface and compare with acceptance criteria.
- Produce final evidence-backed summary and deliverables.

## 11. Failure Recovery
- If validation fails, isolate or revert the latest change and preserve the failing evidence.
- If the verification surface cannot run, report the command, error, missing input, and what would unlock progress.
- If progress stalls, summarize attempted paths and switch only to a lower-risk path supported by evidence.

## 12. Blocked Stop Condition
Stop when the required verification surface cannot be accessed, no valid path remains within the stated boundaries, or further progress would require guessing. Report attempted paths, evidence gathered, blocker, and next input needed.

## 13. Budget / Runtime Limit
Default to five bounded iterations or ask the user before continuing beyond the available evidence/budget.

## 14. Deliverables
- code changes or patch summary
- benchmark before/after evidence
- test output summary

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
