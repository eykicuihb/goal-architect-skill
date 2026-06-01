import importlib.util
import json
import pathlib
import sys
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "goal_architect.py"
spec = importlib.util.spec_from_file_location("goal_architect", SCRIPT)
goal_architect = importlib.util.module_from_spec(spec)
sys.modules["goal_architect"] = goal_architect
spec.loader.exec_module(goal_architect)


class GoalArchitectTests(unittest.TestCase):
    def test_compile_performance_goal_contains_required_fields(self):
        request = "Reduce checkout p95 latency below 120ms while keeping correctness tests green."
        contract = goal_architect.compile_goal(request)
        data = contract.to_dict()
        for key in [
            "outcome",
            "verification_surface",
            "constraints",
            "boundaries",
            "acceptance_criteria",
            "iteration_policy",
            "blocked_stop_condition",
            "quality_score",
        ]:
            self.assertIn(key, data)
        self.assertGreaterEqual(contract.quality_score.verifiability, 8)

    def test_codex_goal_format_starts_with_goal(self):
        contract = goal_architect.compile_goal("Fix the flaky checkout test with evidence.")
        command = goal_architect.contract_to_codex_goal(contract)
        self.assertTrue(command.startswith("/goal "))
        self.assertIn("verified by", command)
        self.assertIn("If blocked", command)

    def test_research_goal_has_uncertainty_language(self):
        contract = goal_architect.compile_goal("Reproduce this paper and separate blocked claims from approximate results.")
        joined = json.dumps(contract.to_dict()).lower()
        self.assertIn("blocked", joined)
        self.assertIn("approximate", joined)
        self.assertIn("evidence", joined)

    def test_critique_weak_goal_recommends_repair(self):
        score = goal_architect.score_goal("Improve the app")
        self.assertEqual(score.drift_risk, "High")
        self.assertLess(score.scope_control, 7)


if __name__ == "__main__":
    unittest.main()
