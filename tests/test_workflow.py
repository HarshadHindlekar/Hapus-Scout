import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from scout.inspection import parse_analysis
from scout.model import validate_model
from scout.service import ScoutService
from scout.storage import CaseStore

# Test doubles only; no fake model exists in the application or demo.
RESULT = dict(summary="Test brief", image_quality="usable", observations=["Test observation"],
              possible_explanations=[], questions=["Test question?"], next_checks=["Collect evidence"],
              limitations=["Test only"], reference_ids=[])


class FakeModel:
    def __init__(self):
        self.prompts = []
        self.fail = False

    def generate(self, image, prompt):
        self.prompts.append(prompt)
        if self.fail:
            raise RuntimeError("Test outage")
        return json.dumps(RESULT)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = CaseStore(self.temp.name)
        self.model = FakeModel()
        self.service = ScoutService(self.store, self.model)

    def new(self):
        return self.service.submit(Image.new("RGB", (40, 40)), "Test tree", "Leaf", "Synthetic observation")

    def test_report_survives_outage_and_restart(self):
        case = self.new()
        self.model.fail = True
        failed = self.service.analyze(case["id"])
        self.assertEqual(failed["analysis_status"], "unavailable")
        self.assertEqual(failed["revisions"], [])
        restarted = CaseStore(self.temp.name)
        self.assertEqual(restarted.get(case["id"])["report"], case["report"])
        self.assertEqual(restarted.photo(case["id"]).size, (40, 40))

    def test_followup_preserves_evidence_and_history(self):
        case = self.new()
        self.service.analyze(case["id"])
        updated = self.service.analyze(case["id"], "Three nearby trees")
        self.assertEqual(len(updated["revisions"]), 2)
        self.assertIn("Three nearby trees", self.model.prompts[-1])
        self.assertIn("Synthetic observation", self.model.prompts[-1])
        self.assertIn("Test question?", self.model.prompts[-1])
        self.store.reviewed(case["id"])
        self.assertEqual(self.store.get(case["id"])["status"], "reviewed")
        self.assertEqual(self.service.analyze(case["id"])["status"], "open")

    def test_failed_followup_keeps_previous_brief(self):
        case = self.new()
        self.service.analyze(case["id"])
        self.model.fail = True
        failed = self.service.analyze(case["id"])
        self.assertEqual(len(failed["revisions"]), 1)
        self.assertEqual(failed["analysis_status"], "unavailable")

    def test_invalid_or_invented_outputs_rejected(self):
        for change in [dict(reference_ids=["invented"]), dict(observations="wrong type"),
                       dict(image_quality="unclear", possible_explanations=["disease"]),
                       dict(questions=["1", "2", "3"])]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                parse_analysis(json.dumps(RESULT | change))

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            self.store.get("../outside")

    def test_incomplete_model_rejected(self):
        folder = Path(self.temp.name)
        (folder / "config.json").write_text('{"model_type":"qwen3_vl"}')
        (folder / "model.safetensors.index.json").write_text('{"weight_map":{"a":"missing.safetensors"}}')
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_model(folder)


if __name__ == "__main__":
    unittest.main()
