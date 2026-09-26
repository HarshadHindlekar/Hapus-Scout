import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.colab_bootstrap import launch


class BootstrapTests(unittest.TestCase):
    def test_temporary_mode_never_imports_drive(self):
        with patch.dict(sys.modules, {"google.colab": None}), \
             patch("scripts.colab_bootstrap.subprocess.run") as run, \
             patch("scout.model.validate_model", return_value=Path("/content/HapusScout/model")):
            launch(use_drive=False)
        self.assertEqual(run.call_count, 3)
        self.assertIn("snapshot_download", run.call_args_list[1].args[0][2])
        env = run.call_args.kwargs["env"]
        self.assertEqual(env["SCOUT_DATA_DIR"], "/content/HapusScout/cases")
        self.assertEqual(env["SCOUT_STORAGE_MODE"], "temporary")

    def test_auth_failure_does_not_silently_download(self):
        module = types.ModuleType("google.colab")
        module.drive = types.SimpleNamespace(mount=lambda _: (_ for _ in ()).throw(RuntimeError("auth failed")))
        with patch.dict(sys.modules, {"google.colab": module}), \
             patch("scripts.colab_bootstrap.subprocess.run") as run:
            with self.assertRaisesRegex(RuntimeError, "USE_DRIVE = False"):
                launch()
            run.assert_not_called()
