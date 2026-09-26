"""Executed by the single launcher cell, after cloning this repository."""
import os
import subprocess
import sys
from pathlib import Path


def launch(model_path="", use_drive=True):
    if use_drive:
        from google.colab import drive
        try:
            drive.mount("/content/drive")
        except Exception as exc:
            raise RuntimeError("Google Drive authentication failed before model loading. "
                               "To run without Drive, set USE_DRIVE = False in the launcher. "
                               "That downloads the public model and saves cases temporarily in Colab.") from exc
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(root / "requirements.txt")], check=True)
    # Model discovery is dependency-light and only reads config / shard metadata.
    sys.path.insert(0, str(root))
    from scout.model import discover_model, validate_model
    preferred = Path("/content/drive/MyDrive/Hapus More AI/models/model-00001-of-00002.safetensors")
    if not use_drive:
        print("Drive-free mode: model and cases use temporary Colab storage. "
              "Cases are lost when the runtime is deleted. Downloading the public model may take several minutes.", flush=True)
        model = Path("/content/HapusScout/model")
        subprocess.run([sys.executable, "-c",
                        "from huggingface_hub import snapshot_download; "
                        "snapshot_download('Qwen/Qwen3-VL-4B-Instruct', "
                        "local_dir='/content/HapusScout/model', "
                        "allow_patterns=['*.json', '*.safetensors', '*.txt', '*.jinja', '*.model'])"], check=True)
        model = validate_model(model)
    elif model_path.strip():
        model = validate_model(model_path)
    elif (preferred / "config.json").exists():
        model = validate_model(preferred)
    else:
        model = discover_model("/content/drive/MyDrive")
    env = os.environ.copy()
    env["SCOUT_MODEL_PATH"] = str(model)
    env["SCOUT_DATA_DIR"] = "/content/drive/MyDrive/HapusScout/cases" if use_drive else "/content/HapusScout/cases"
    env["SCOUT_STORAGE_MODE"] = "drive" if use_drive else "temporary"
    env["GRADIO_ANALYTICS_ENABLED"] = "False"
    print("Model found. Starting Hapus Scout; keep this cell running.", flush=True)
    subprocess.run([sys.executable, str(root / "app.py"), "--share"], cwd=root, env=env, check=True)
