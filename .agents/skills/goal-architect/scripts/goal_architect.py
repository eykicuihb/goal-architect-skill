#!/usr/bin/env python3
"""
Goal Architect deterministic helper.

This script compiles a vague request into a first-pass Goal Contract or a compact
Codex /goal command. It intentionally uses only Python stdlib so it can run
inside most coding-agent environments without setup.

It is not a replacement for model judgment. Treat the output as a draft and
tighten it before activation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Dict, Any


ACTION_WORDS = {
    "fix", "debug", "reduce", "increase", "implement", "migrate", "refactor",
    "reproduce", "verify", "stabilize", "optimize", "improve", "write", "produce",
    "add", "remove", "upgrade", "audit", "investigate", "analyze"
}

VERIFICATION_KEYWORDS = {
    "test", "tests", "benchmark", "benchmarks", "pytest", "unit", "integration",
    "e2e", "snapshot", "lint", "typecheck", "coverage", "report", "artifact",
    "logs", "metrics", "dashboard", "trace", "profile", "reproduction", "build"
}

CONSTRAINT_KEYWORDS = {
    "without", "preserve", "no", "must not", "avoid", "compatible", "zero downtime",
    "do not", "keep", "unchanged", "regression", "not regress"
}

RESEARCH_KEYWORDS = {
    "paper", "research", "reproduce", "replicate", "claim", "evidence", "audit",
    "experiment", "result", "dataset", "baseline"
}

PERFORMANCE_KEYWORDS = {
    "latency", "p95", "p99", "performance", "throughput", "benchmark", "slow",
    "speed", "memory", "cpu", "hot path", "profile"
}

BUG_TEST_KEYWORDS = {
    "bug", "flaky", "failing", "failure", "test", "regression", "crash", "error",
    "exception", "timeout"
}

REFACTOR_KEYWORDS = {
    "refactor", "cleanup", "architecture", "complexity", "maintenance", "module",
    "debt", "simplify"
}

DOC_KEYWORDS = {
    "docs", "documentation", "readme", "guide", "manual", "tutorial", "page"
}


@dataclass
class QualityScore:
    clarity: float
    verifiability: float
    scope_control: float
    autonomy_readiness: float
    drift_risk: str
    overall: float


@dataclass
class Boundaries:
    in_scope: List[str]
    out_of_scope: List[str]


@dataclass
class GoalContract:
    outcome: str
    business_value: str
    verification_surface: List[str]
    constraints: List[str]
    boundaries: Boundaries
    required_context: List[str]
    assumptions: List[str]
    acceptance_criteria: List[str]
    iteration_policy: List[str]
    checkpoints: List[str]
    failure_recovery: List[str]
    blocked_stop_condition: str
    budget_runtime_limit: str
    deliverables: List[str]
    risk_level: str
    estimated_runtime: str
    quality_score: QualityScore

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    lower = text.lower()
    return any(k in lower for k in keywords)


def sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?。！？])\s+|\n+", text.strip())
    return [normalize(p) for p in parts if normalize(p)]


def extract_metrics(text: str) -> List[str]:
    patterns = [
        r"\bp\d{2}\b[^,.;\n]*?(?:<|<=|below|under|less than|within|to)\s*\d+(?:\.\d+)?\s*(?:ms|s|sec|seconds|%)?",
        r"\b(?:below|under|less than|within|to|from)\s*\d+(?:\.\d+)?\s*(?:ms|s|sec|seconds|%|x)?",
        r"\b\d+(?:\.\d+)?\s*(?:ms|s|sec|seconds|%|x)\b",
        r"\b\d+\s*(?:iterations|attempts|runs|days|hours|minutes)\b",
    ]
    results: List[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.I):
            value = normalize(match if isinstance(match, str) else " ".join(match))
            if value and value not in results:
                results.append(value)
    return dedupe_substrings(results)


def extract_files_or_scopes(text: str) -> List[str]:
    scopes: List[str] = []
    for match in re.findall(r"(?:[\w.-]+/)+(?:[\w.-]+)", text):
        if match not in scopes:
            scopes.append(match)
    for match in re.findall(r"\b[\w.-]+\.(?:py|ts|tsx|js|jsx|go|rs|java|kt|swift|md|yml|yaml|json|toml|sql|sh)\b", text):
        if match not in scopes:
            scopes.append(match)
    quoted = re.findall(r"[`'\"]([^`'\"]{3,80})[`'\"]", text)
    for item in quoted:
        if any(token in item for token in ["/", ".py", ".ts", ".md", "service", "module", "repo"]):
            if item not in scopes:
                scopes.append(item)
    return scopes


def classify(text: str) -> str:
    if contains_any(text, RESEARCH_KEYWORDS):
        return "research"
    if contains_any(text, PERFORMANCE_KEYWORDS):
        return "performance"
    if contains_any(text, BUG_TEST_KEYWORDS):
        return "bug_or_test"
    if contains_any(text, REFACTOR_KEYWORDS):
        return "refactor"
    if contains_any(text, DOC_KEYWORDS):
        return "docs"
    return "general"


def infer_outcome(text: str, task_type: str, metrics: List[str]) -> str:
    first = sentences(text)[0] if sentences(text) else normalize(text)
    first = first[:260].strip()
    if task_type == "performance" and metrics:
        return f"Achieve the requested performance target ({'; '.join(metrics[:2])}) for the relevant system while preserving correctness."
    if task_type == "research":
        return "Produce the strongest evidence-backed reproduction or audit of the requested research claims using the available materials and local resources."
    if task_type == "bug_or_test":
        return "Resolve or explain the failing behavior with evidence from reproduction steps, tests, logs, or command output."
    if task_type == "refactor":
        return "Complete the requested refactor while preserving existing externally observable behavior."
    if task_type == "docs":
        return "Produce the requested documentation artifact and verify it matches current behavior or source material."
    return first if len(first) >= 20 else "Transform the user's request into a concrete, evidence-backed deliverable with bounded execution."


def infer_business_value(task_type: str) -> str:
    return {
        "performance": "Improve user experience and operational efficiency without sacrificing correctness.",
        "research": "Reduce uncertainty by separating confirmed evidence, approximate reconstruction, blocked claims, and remaining unknowns.",
        "bug_or_test": "Restore reliability and prevent the same failure from recurring unnoticed.",
        "refactor": "Reduce maintenance cost while protecting current behavior.",
        "docs": "Make the feature easier to understand, operate, and validate.",
        "general": "Convert ambiguous intent into an auditable execution target.",
    }[task_type]


def infer_verification_surface(text: str, task_type: str) -> List[str]:
    surfaces: List[str] = []
    lowered = text.lower()
    if "pytest" in lowered:
        surfaces.append("`pytest` output for the relevant test suite")
    if "benchmark" in lowered or task_type == "performance":
        surfaces.append("benchmark output showing the target metric is met")
    if "lint" in lowered:
        surfaces.append("lint output with no new violations")
    if "type" in lowered or "typecheck" in lowered:
        surfaces.append("typecheck output with no new errors")
    if task_type == "bug_or_test":
        surfaces.extend(["reproduction steps or failing test before the fix", "passing test output after the fix"])
    elif task_type == "research":
        surfaces.extend(["claim inventory mapped to available evidence", "final audit report separating confirmed, approximate, proxy-supported, blocked, and uncertain claims"])
    elif task_type == "refactor":
        surfaces.extend(["existing unit and integration tests", "API or behavior parity checks"])
    elif task_type == "docs":
        surfaces.extend(["generated documentation artifact", "local docs build or review checklist"])
    else:
        surfaces.extend(["explicit acceptance checklist", "final evidence-backed report"])
    return dedupe(surfaces)


def infer_constraints(text: str, task_type: str) -> List[str]:
    constraints: List[str] = []
    lowered = text.lower()
    lowered = text.lower()
    if "don't break correctness" in lowered or "do not break correctness" in lowered or "not regress correctness" in lowered:
        constraints.append("Do not regress correctness tests.")
    elif contains_any(text, CONSTRAINT_KEYWORDS):
        for s in sentences(text):
            if contains_any(s, CONSTRAINT_KEYWORDS):
                # Avoid turning a long vague request into a constraint. Keep it only if it is already constraint-shaped.
                if len(s) < 140 or s.lower().startswith(("without", "preserve", "do not", "must not", "no ", "keep")):
                    constraints.append(s)
    if task_type == "performance":
        constraints.append("Do not regress correctness tests or public behavior.")
    elif task_type == "bug_or_test":
        constraints.append("Do not mask the failure by deleting or weakening relevant tests unless explicitly justified.")
    elif task_type == "refactor":
        constraints.append("Preserve public APIs, data contracts, and existing behavior unless explicitly in scope.")
    elif task_type == "research":
        constraints.append("Do not overstate unsupported claims; label proxy evidence and blocked claims honestly.")
    elif task_type == "docs":
        constraints.append("Do not document behavior that cannot be traced to current source, commands, or authoritative material.")
    else:
        constraints.append("Do not expand scope beyond the user request without explicit justification.")
    if "database" not in lowered and task_type in {"refactor", "bug_or_test"}:
        constraints.append("Avoid database schema changes unless explicitly required and approved.")
    return dedupe(constraints)


def infer_boundaries(text: str, task_type: str) -> Boundaries:
    scopes = extract_files_or_scopes(text)
    if scopes:
        in_scope = scopes
    elif task_type == "performance":
        in_scope = ["current repository", "relevant service/module", "benchmark fixtures", "related tests"]
    elif task_type == "research":
        in_scope = ["provided paper/materials", "available datasets/code", "local reproducible experiments", "final audit report"]
    elif task_type == "docs":
        in_scope = ["documentation files", "source files needed to verify behavior", "docs build tooling"]
    else:
        in_scope = ["current repository", "files directly related to the requested task", "relevant tests and documentation"]

    out_of_scope = [
        "unrelated rewrites",
        "large architectural changes not required by the Goal",
        "speculative work without evidence",
    ]
    if task_type != "research":
        out_of_scope.append("changes outside the relevant module unless evidence shows they are necessary")
    return Boundaries(in_scope=dedupe(in_scope), out_of_scope=dedupe(out_of_scope))


def infer_required_context(text: str, task_type: str) -> List[str]:
    contexts = extract_files_or_scopes(text)
    if task_type == "performance":
        contexts.extend(["benchmark command and baseline result", "correctness test command"])
    elif task_type == "bug_or_test":
        contexts.extend(["reproduction command or failing test", "relevant logs or stack trace"])
    elif task_type == "research":
        contexts.extend(["source paper or research materials", "available code/data/checkpoints", "local environment constraints"])
    elif task_type == "refactor":
        contexts.extend(["current module behavior", "test suite", "public API or compatibility expectations"])
    elif task_type == "docs":
        contexts.extend(["current source behavior", "docs build command", "target audience"])
    else:
        contexts.extend(["relevant repository files", "validation command or review checklist"])
    return dedupe(contexts)


def infer_acceptance(text: str, task_type: str, metrics: List[str]) -> List[str]:
    criteria: List[str] = []
    if metrics:
        criteria.append(f"Target metric is met: {'; '.join(metrics[:3])}.")
    if task_type == "performance":
        criteria.extend([
            "Benchmark output demonstrates the performance target is met on the agreed benchmark.",
            "Correctness test suite remains green.",
        ])
    elif task_type == "bug_or_test":
        criteria.extend([
            "The failure is reproduced or the inability to reproduce is documented with commands and evidence.",
            "A relevant test passes after the fix or the blocker is clearly explained.",
        ])
    elif task_type == "research":
        criteria.extend([
            "A claim inventory maps each major claim to evidence status.",
            "Final report separates exact reproduction, approximate reconstruction, proxy support, blocked claims, and uncertainty.",
        ])
    elif task_type == "refactor":
        criteria.extend([
            "Existing behavior is preserved according to tests or parity checks.",
            "The refactor produces a smaller, clearer, or better-isolated implementation without broad unrelated changes.",
        ])
    elif task_type == "docs":
        criteria.extend([
            "Documentation artifact exists and covers the requested feature or workflow.",
            "Docs build or review checklist passes.",
        ])
    else:
        criteria.extend([
            "All explicitly requested deliverables are produced.",
            "Completion is supported by concrete evidence rather than assertion.",
        ])
    return dedupe(criteria)


def infer_checkpoints(task_type: str) -> List[str]:
    common = [
        "Establish baseline/current state and capture evidence.",
        "Identify the smallest high-confidence next action.",
        "Apply or propose one bounded intervention.",
        "Run the verification surface and compare with acceptance criteria.",
        "Produce final evidence-backed summary and deliverables.",
    ]
    if task_type == "research":
        return [
            "Inventory the target claims and required evidence.",
            "Map available materials, code, data, and local constraints.",
            "Attempt feasible reproductions or reconstructions.",
            "Label unsupported or blocked claims with missing inputs.",
            "Produce final audit with confidence levels and remaining uncertainty.",
        ]
    return common


def infer_deliverables(task_type: str) -> List[str]:
    if task_type == "performance":
        return ["code changes or patch summary", "benchmark before/after evidence", "test output summary"]
    if task_type == "bug_or_test":
        return ["root-cause summary", "fix or blocker report", "test/log evidence"]
    if task_type == "research":
        return ["claim inventory", "reproducibility artifacts where feasible", "evidence-backed audit report"]
    if task_type == "refactor":
        return ["refactored implementation", "parity/test evidence", "migration or review notes"]
    if task_type == "docs":
        return ["documentation artifact", "build/review evidence", "list of verified commands or examples"]
    return ["completed artifact", "evidence-backed completion report"]


def infer_risk(text: str, task_type: str) -> str:
    lowered = text.lower()
    high_markers = ["production", "database", "security", "auth", "payments", "migration", "zero downtime"]
    if any(m in lowered for m in high_markers):
        return "High"
    if task_type in {"refactor", "research", "performance"}:
        return "Medium"
    return "Low"


def infer_runtime(task_type: str, metrics: List[str]) -> str:
    if task_type in {"research", "performance"}:
        return "Long"
    if task_type in {"refactor", "bug_or_test"}:
        return "Medium"
    return "Short" if not metrics else "Medium"


def dedupe(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        normalized = normalize(item)
        if normalized and normalized.lower() not in seen:
            out.append(normalized)
            seen.add(normalized.lower())
    return out


def dedupe_substrings(items: Iterable[str]) -> List[str]:
    normalized = dedupe(items)
    result: List[str] = []
    for item in sorted(normalized, key=len, reverse=True):
        lower = item.lower()
        if not any(lower != kept.lower() and lower in kept.lower() for kept in result):
            result.append(item)
    return sorted(result, key=lambda x: normalized.index(x))


def score_goal(text: str, contract: GoalContract | None = None) -> QualityScore:
    source = text
    if contract:
        source = json.dumps(contract.to_dict(), ensure_ascii=False)

    has_metric = bool(extract_metrics(source)) or contains_any(source, VERIFICATION_KEYWORDS)
    has_boundary = contains_any(source, {"scope", "only", "use only", "in scope", "out of scope", "non-goal", "boundary"})
    has_constraint = contains_any(source, CONSTRAINT_KEYWORDS)
    has_stop = contains_any(source, {"stop", "blocked", "budget", "no valid path", "no defensible path"})
    has_iteration = contains_any(source, {"between iterations", "after each", "next", "continue", "attempt"})

    clarity = 6.0 + (1.0 if len(normalize(source)) > 80 else 0) + (1.0 if any(w in source.lower() for w in ACTION_WORDS) else 0) + (1.0 if has_metric else 0)
    verifiability = 5.0 + (2.5 if has_metric else 0) + (1.0 if "evidence" in source.lower() else 0) + (1.0 if contains_any(source, VERIFICATION_KEYWORDS) else 0)
    scope_control = 5.0 + (2.0 if has_boundary else 0) + (1.0 if has_constraint else 0) + (1.0 if "out of scope" in source.lower() or "non-goal" in source.lower() else 0)
    autonomy = 5.0 + (1.5 if has_iteration else 0) + (1.5 if has_stop else 0) + (1.0 if "deliverable" in source.lower() or "report" in source.lower() else 0)

    clarity = min(10.0, round(clarity, 1))
    verifiability = min(10.0, round(verifiability, 1))
    scope_control = min(10.0, round(scope_control, 1))
    autonomy = min(10.0, round(autonomy, 1))

    if not has_stop or not has_boundary:
        drift = "High"
    elif min(verifiability, scope_control, autonomy) < 7:
        drift = "Medium"
    else:
        drift = "Low"

    overall = round((clarity + verifiability + scope_control + autonomy) / 4, 1)
    return QualityScore(clarity, verifiability, scope_control, autonomy, drift, overall)


def compile_goal(text: str) -> GoalContract:
    text = normalize(text)
    task_type = classify(text)
    metrics = extract_metrics(text)
    outcome = infer_outcome(text, task_type, metrics)
    boundaries = infer_boundaries(text, task_type)

    contract = GoalContract(
        outcome=outcome,
        business_value=infer_business_value(task_type),
        verification_surface=infer_verification_surface(text, task_type),
        constraints=infer_constraints(text, task_type),
        boundaries=boundaries,
        required_context=infer_required_context(text, task_type),
        assumptions=[
            "The current repository or provided materials contain enough context to inspect and validate the task.",
            "If a required command, dataset, credential, or environment is unavailable, the agent will report the blocker instead of fabricating success.",
        ],
        acceptance_criteria=infer_acceptance(text, task_type, metrics),
        iteration_policy=[
            "After each attempt, record what was inspected or changed.",
            "Record the evidence observed from tests, benchmarks, logs, artifacts, source material, or review checklist.",
            "Compare the latest evidence against the acceptance criteria before deciding whether to continue.",
            "Choose the next lowest-risk action that most directly improves evidence toward completion.",
            "Do not continue if the next action would exceed scope, budget, or available evidence.",
        ],
        checkpoints=infer_checkpoints(task_type),
        failure_recovery=[
            "If validation fails, isolate or revert the latest change and preserve the failing evidence.",
            "If the verification surface cannot run, report the command, error, missing input, and what would unlock progress.",
            "If progress stalls, summarize attempted paths and switch only to a lower-risk path supported by evidence.",
        ],
        blocked_stop_condition=(
            "Stop when the required verification surface cannot be accessed, no valid path remains within the stated boundaries, "
            "or further progress would require guessing. Report attempted paths, evidence gathered, blocker, and next input needed."
        ),
        budget_runtime_limit="Default to five bounded iterations or ask the user before continuing beyond the available evidence/budget.",
        deliverables=infer_deliverables(task_type),
        risk_level=infer_risk(text, task_type),
        estimated_runtime=infer_runtime(task_type, metrics),
        quality_score=QualityScore(0, 0, 0, 0, "Medium", 0),
    )
    contract.quality_score = score_goal(text, contract)
    return contract


def contract_to_markdown(contract: GoalContract) -> str:
    b = contract.boundaries
    q = contract.quality_score

    def bullets(items: List[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- TBD"

    return f"""# Goal Contract

## 1. Outcome
{contract.outcome}

## 2. Business / User Value
{contract.business_value}

## 3. Verification Surface
{bullets(contract.verification_surface)}

## 4. Constraints
{bullets(contract.constraints)}

## 5. Boundaries
### In Scope
{bullets(b.in_scope)}

### Out of Scope / Non-Goals
{bullets(b.out_of_scope)}

## 6. Required Context
{bullets(contract.required_context)}

## 7. Assumptions
{bullets(contract.assumptions)}

## 8. Acceptance Criteria
{bullets(contract.acceptance_criteria)}

## 9. Iteration Policy
{bullets(contract.iteration_policy)}

## 10. Checkpoints
{bullets(contract.checkpoints)}

## 11. Failure Recovery
{bullets(contract.failure_recovery)}

## 12. Blocked Stop Condition
{contract.blocked_stop_condition}

## 13. Budget / Runtime Limit
{contract.budget_runtime_limit}

## 14. Deliverables
{bullets(contract.deliverables)}

## 15. Risk Level
{contract.risk_level}

## 16. Estimated Runtime
{contract.estimated_runtime}

## 17. Goal Quality Score
- clarity: {q.clarity}/10
- verifiability: {q.verifiability}/10
- scope_control: {q.scope_control}/10
- autonomy_readiness: {q.autonomy_readiness}/10
- drift_risk: {q.drift_risk}
- overall: {q.overall}/10
"""


def contract_to_codex_goal(contract: GoalContract) -> str:
    outcome = contract.outcome.rstrip(".")
    evidence = "; ".join(item.rstrip(".") for item in contract.verification_surface[:3])
    constraints = "; ".join(item.rstrip(".") for item in contract.constraints[:3])
    boundaries = "; ".join(item.rstrip(".") for item in contract.boundaries.in_scope[:4])
    return (
        f"/goal {outcome}, verified by {evidence}, while preserving {constraints}. "
        f"Use only {boundaries}. Between iterations, record what was inspected or changed, "
        f"the evidence observed, and the next lowest-risk action. If blocked or no valid paths remain, "
        f"stop with attempted paths, gathered evidence, blocker, and next input needed."
    )


def read_input(path: str | None) -> str:
    if not path or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def cmd_compile(args: argparse.Namespace) -> int:
    raw = read_input(args.input)
    if not normalize(raw):
        print("No input provided.", file=sys.stderr)
        return 2
    contract = compile_goal(raw)
    if args.format == "json":
        print(json.dumps(contract.to_dict(), ensure_ascii=False, indent=2))
    elif args.format == "codex":
        print(contract_to_codex_goal(contract))
    else:
        print(contract_to_markdown(contract))
    return 0


def cmd_critique(args: argparse.Namespace) -> int:
    raw = read_input(args.input)
    q = score_goal(raw)
    issues: List[str] = []
    if q.verifiability < 8:
        issues.append("Verification surface is weak or missing. Add tests, benchmark, artifact, logs, or source evidence.")
    if q.scope_control < 7:
        issues.append("Scope boundaries are weak. Add in-scope resources and explicit non-goals.")
    if q.autonomy_readiness < 7:
        issues.append("Autonomy readiness is weak. Add iteration policy, blocked stop condition, and deliverables.")
    if q.drift_risk == "High":
        issues.append("High drift risk. Add budget/runtime limit and no-progress stop condition.")

    result = {
        "quality_score": asdict(q),
        "issues": issues or ["No major issues detected by heuristic scorer."],
        "activation_recommendation": "activate" if q.clarity >= 8 and q.verifiability >= 8 and q.scope_control >= 7 and q.autonomy_readiness >= 7 and q.drift_risk != "High" else "repair_before_activation",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile vague intent into a Codex-style Goal Contract.")
    sub = parser.add_subparsers(dest="command", required=True)

    compile_p = sub.add_parser("compile", help="Compile a request into a Goal Contract.")
    compile_p.add_argument("input", nargs="?", default="-", help="Input file path or '-' for stdin.")
    compile_p.add_argument("--format", choices=["markdown", "json", "codex"], default="markdown")
    compile_p.set_defaults(func=cmd_compile)

    critique_p = sub.add_parser("critique", help="Score and critique an existing Goal.")
    critique_p.add_argument("input", nargs="?", default="-", help="Input file path or '-' for stdin.")
    critique_p.set_defaults(func=cmd_critique)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
