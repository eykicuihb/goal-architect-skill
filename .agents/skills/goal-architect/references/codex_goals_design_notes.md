# Codex Goal Design Notes

A Goal is best treated as a thread-scoped completion contract, not as a larger prompt.

A strong Goal includes:

1. Outcome
2. Verification surface
3. Constraints
4. Boundaries
5. Iteration policy
6. Blocked stop condition

The agent should continue only when evidence says the Goal is not complete, the Goal is still active, no user input is pending, and budget remains.

Completion must be based on evidence, not model belief.

Good evidence includes:

- test output
- benchmark output
- logs
- command output
- generated artifacts
- changed files / diffs
- source material
- final reports with claim-to-evidence mapping

Budget limit is not success. When budget is reached, the agent should stop substantive work and summarize progress, blockers, and next useful step.

For research Goals, distinguish:

- confirmed claims
- approximate reconstructions
- proxy support
- blocked claims
- remaining uncertainty
