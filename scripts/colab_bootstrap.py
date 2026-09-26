"""Executed by the single launcher cell, after cloning this repository."""
import os
import subprocess
import sys
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from time import monotonic


def stream_command(command, **kwargs):
    """Forward child output through notebook stdout, including errors and the demo URL."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1, **kwargs)
    messages = Queue()

    def read():
        try:
            for line in process.stdout:
                messages.put(line)
        finally:
            messages.put(None)

    Thread(target=read, daemon=True).start()
    started = monotonic()
    try:
        while True:
            try:
                line = messages.get(timeout=30)
            except Empty:
                print(f"Process still running ({int(monotonic() - started)}s); waiting for its next log message.", flush=True)
                continue
            if line is None:
                break
            print(line, end="", flush=True)
        result = process.wait()
        if result:
            raise subprocess.CalledProcessError(result, command)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        process.stdout.close()


def launch(model_path="", use_drive=True, ui_only=False):
    if use_drive and not ui_only:
        from google.colab import drive
        try:
            drive.mount("/content/drive")
        except Exception as exc:
            raise RuntimeError("Google Drive authentication failed before model loading. "
                               "To run without Drive, set USE_DRIVE = False in the launcher. "
                               "That downloads the public model and saves cases temporarily in Colab.") from exc
    root = Path(__file__).resolve().parents[1]
    print("Step 1/3: checking Python dependencies.", flush=True)
    stream_command([sys.executable, "-u", "-m", "pip", "install", "-q", "-r", str(root / "requirements.txt")])
    # Model discovery is dependency-light and only reads config / shard metadata.
    sys.path.insert(0, str(root))
    
    env = os.environ.copy()
    if not ui_only:
        from scout.model import discover_model, validate_model
        preferred = Path("/content/drive/MyDrive/Hapus More AI/models/model-00001-of-00002.safetensors")
        if not use_drive:
            print("Drive-free mode: model and cases use temporary Colab storage. "
                  "Cases are lost when the runtime is deleted. Downloading the public model may take several minutes.", flush=True)
            model = Path("/content/HapusScout/model")
            stream_command([sys.executable, "-u", "-c",
                            "from huggingface_hub import snapshot_download; "
                            "snapshot_download('Qwen/Qwen3-VL-4B-Instruct', "
                            "local_dir='/content/HapusScout/model', "
                            "allow_patterns=['*.json', '*.safetensors', '*.txt', '*.jinja', '*.model'])"])
            model = validate_model(model)
        elif model_path.strip():
            model = validate_model(model_path)
        elif (preferred / "config.json").exists():
            model = validate_model(preferred)
        else:
            model = discover_model("/content/drive/MyDrive")
        env["SCOUT_MODEL_PATH"] = str(model)

    env["SCOUT_DATA_DIR"] = "/content/drive/MyDrive/HapusScout/cases" if (use_drive and not ui_only) else "/content/HapusScout/cases"
    env["SCOUT_STORAGE_MODE"] = "drive" if (use_drive and not ui_only) else "temporary"
    env["GRADIO_ANALYTICS_ENABLED"] = "False"
    print("\n=======================================================", flush=True)
    print("Step 2/3: Launching application interface...", flush=True)
    if not ui_only:
        print("[INFO] GPU model allocation starting now (~30-45 seconds).", flush=True)
        print("-> DO NOT CLICK STOP OR INTERRUPT IN COLAB. Please wait for the link below!", flush=True)
    else:
        print("[INFO] UI-Only Fast Mode Enabled. Interface starting in ~2 seconds...", flush=True)
    print("=======================================================\n", flush=True)
    env["PYTHONUNBUFFERED"] = "1"
    cmd = [sys.executable, "-u", str(root / "app.py"), "--share"]
    if ui_only:
        cmd.append("--ui-only")
    stream_command(cmd, cwd=root, env=env)
