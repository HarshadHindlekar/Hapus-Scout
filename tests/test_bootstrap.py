import sys
import types
import unittest
import io
import subprocess
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from scripts.colab_bootstrap import launch, stream_command


class BootstrapTests(unittest.TestCase):
    def test_temporary_mode_never_imports_drive(self):
        with patch.dict(sys.modules, {"google.colab": None}), \
             patch("scripts.colab_bootstrap.stream_command") as run, \
             patch("scout.model.validate_model", return_value=Path("/content/HapusScout/model")):
            launch(use_drive=False)
        self.assertEqual(run.call_count, 3)
        self.assertIn("snapshot_download", run.call_args_list[1].args[0][3])
        env = run.call_args.kwargs["env"]
        self.assertEqual(env["SCOUT_DATA_DIR"], "/content/HapusScout/cases")
        self.assertEqual(env["SCOUT_STORAGE_MODE"], "temporary")

    def test_auth_failure_does_not_silently_download(self):
        module = types.ModuleType("google.colab")
        module.drive = types.SimpleNamespace(mount=lambda _: (_ for _ in ()).throw(RuntimeError("auth failed")))
        with patch.dict(sys.modules, {"google.colab": module}), \
             patch("scripts.colab_bootstrap.stream_command") as run:
            with self.assertRaisesRegex(RuntimeError, "USE_DRIVE = False"):
                launch()
            run.assert_not_called()

    def test_child_output_reaches_notebook_stdout(self):
        output = io.StringIO()
        with redirect_stdout(output):
            stream_command([sys.executable, "-u", "-c", "import sys; print('ready'); print('error detail', file=sys.stderr)"])
        self.assertIn("ready", output.getvalue())
        self.assertIn("error detail", output.getvalue())

    def test_child_failure_is_not_hidden(self):
        with redirect_stdout(io.StringIO()), self.assertRaises(subprocess.CalledProcessError):
            stream_command([sys.executable, "-c", "raise SystemExit(7)"])
