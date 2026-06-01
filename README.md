# Goal Architect Skill

Goal Architect turns vague human intent into structured, verifiable autonomous-agent Goals.

This package is ready to copy into a Codex-compatible repository or your user-level skills folder.

## What is included

```text
.agents/skills/goal-architect/
  SKILL.md                         # Codex skill instructions
  agents/openai.yaml               # Optional Codex UI / invocation metadata
  assets/goal_contract_template.md # Full contract template
  assets/codex_goal_template.txt   # Compact /goal template
  references/codex_goals_design_notes.md
  schemas/goal_contract.schema.json
  scripts/goal_architect.py        # Deterministic helper CLI, stdlib only
  tests/test_goal_architect.py
examples/
  vague_request.md
  compiled_goal_contract.md
  codex_goal.txt
  research_request.md
  research_goal_contract.md
install.sh
```

## Install into a repo

From your repository root:

```bash
cp -R .agents/skills/goal-architect .agents/skills/
```

Or unzip this package at the root of the repo. Codex scans `.agents/skills` from the current directory upward.

## Install as a user-level skill

```bash
./install.sh
```

This copies the skill to:

```text
$HOME/.agents/skills/goal-architect
```

## Use inside Codex

Explicit invocation:

```text
$goal-architect Turn this into a strong /goal: reduce checkout p95 below 120ms without regressing correctness tests.
```

Or ask normally; the skill description is written for implicit matching when the task is about creating, repairing, or scoring Goals.

## Use the local deterministic helper

Compile a vague request into a full Markdown contract:

```bash
python .agents/skills/goal-architect/scripts/goal_architect.py compile examples/vague_request.md --format markdown
```

Generate a compact Codex `/goal`:

```bash
python .agents/skills/goal-architect/scripts/goal_architect.py compile examples/vague_request.md --format codex
```

Score an existing Goal:

```bash
python .agents/skills/goal-architect/scripts/goal_architect.py critique examples/codex_goal.txt
```

Run tests:

```bash
python -m unittest discover .agents/skills/goal-architect/tests
```

## Design principles

A strong Goal includes:

1. Outcome
2. Verification surface
3. Constraints
4. Boundaries
5. Iteration policy
6. Blocked stop condition

The agent should not declare success based on confidence alone. Completion must be backed by concrete evidence: tests, benchmark output, logs, changed files, generated artifacts, source material, or a claim-to-evidence audit.

## Recommended activation gate

Only activate a Goal directly when the score meets:

- clarity >= 8
- verifiability >= 8
- scope_control >= 7
- autonomy_readiness >= 7
- drift_risk != High

Otherwise, repair first.
