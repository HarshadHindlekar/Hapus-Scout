"""Executed by the single launcher cell, after cloning this repository."""
import os
import subprocess
import sys
from pathlib import Path


def launch(model_path=""):
    from google.colab import drive
    drive.mount("/content/drive")
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(root / "requirements.txt")], check=True)
    # Model discovery is dependency-light and only reads config / shard metadata.
    sys.path.insert(0, str(root))
    from scout.model import discover_model, validate_model
    preferred = Path("/content/drive/MyDrive/Hapus More AI/models/model-00001-of-00002.safetensors")
    if model_path.strip():
        model = validate_model(model_path)
    elif (preferred / "config.json").exists():
        model = validate_model(preferred)
    else:
        model = discover_model("/content/drive/MyDrive")
    env = os.environ.copy()
    env["SCOUT_MODEL_PATH"] = str(model)
    env["SCOUT_DATA_DIR"] = "/content/drive/MyDrive/HapusScout/cases"
    env["GRADIO_ANALYTICS_ENABLED"] = "False"
    print("Model found. Starting Hapus Scout; keep this cell running.", flush=True)
    subprocess.run([sys.executable, str(root / "app.py"), "--share"], cwd=root, env=env, check=True)
