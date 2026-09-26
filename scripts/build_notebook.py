"""Regenerate the committed single-cell Colab launcher."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = '''# Select Runtime > Change runtime type > T4 GPU before running.
USE_DRIVE = True  # Set False if Google Drive authorization fails; cases become temporary.
MODEL_PATH = ""  # Optional: exact /content/drive/MyDrive/... model folder

import subprocess, sys
from pathlib import Path
repo = Path("/content/Hapus-Scout")
if not (repo / ".git").exists():
    subprocess.run(["git", "clone", "https://github.com/HarshadHindlekar/Hapus-Scout.git", str(repo)], check=True)
else:
    subprocess.run(["git", "-C", str(repo), "pull", "--ff-only"], check=True)
sys.path.insert(0, str(repo))
import runpy
runpy.run_path(str(repo / "scripts/colab_bootstrap.py"))["launch"](MODEL_PATH, use_drive=USE_DRIVE)
'''
notebook = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"colab": {"name": "Hapus Scout - one-cell launch"}, "accelerator": "GPU",
                 "kernelspec": {"name": "python3", "display_name": "Python 3"}},
    "cells": [
        {"id": "instructions", "cell_type": "markdown", "metadata": {}, "source": [
            "# Hapus Scout\n", "Run the entire orchard inspection app in Colab.\n\n",
            "1. Select a **T4 GPU** runtime.\n", "2. Run the cell and mount the Drive account containing your Qwen model.\n",
            "3. Open the printed Gradio link and sign in with the temporary login.\n\n",
            "Keep the cell running. Cases are saved in MyDrive/HapusScout/cases. Use only permitted demo images.\n",
            "If automatic discovery finds zero or multiple models, enter the exact mounted folder in MODEL_PATH.\n",
            "If Drive authorization fails, set USE_DRIVE = False. This downloads Qwen into Colab; model files and cases are temporary and disappear when the runtime is deleted.\n",
            "Inspection support only; live model quality must be verified.\n"]},
        {"id": "launch", "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
         "source": source.splitlines(keepends=True)}]}
(root / "notebooks").mkdir(exist_ok=True)
(root / "notebooks/launch_colab.ipynb").write_text(json.dumps(notebook, indent=2), encoding="utf-8")
compile(source, "colab_cell", "exec")
print("Notebook generated; launcher cell syntax valid.")
