# Hapus Scout

An orchard inspection assistant for Alphonso mango teams. A worker submits a photo and observation; Qwen asks for missing evidence and prepares a manager inspection brief.

**One repository. One Colab runtime. One demo link.** UI and model run together; model files and cases remain in Google Drive.

[Open the launcher in Colab](https://colab.research.google.com/github/HarshadHindlekar/Hapus-Scout/blob/main/notebooks/launch_colab.ipynb)

## Start

1. Open the launcher and select **Runtime > Change runtime type > T4 GPU**.
2. Run its single code cell. Mount the Google account containing the model and approve Drive access yourself.
3. The launcher installs dependencies, locates a complete Qwen3-VL model, loads it and prints a Gradio URL plus a temporary demo login. Keep the cell running.
4. Open that URL and sign in. Use permitted photos and fictional orchard IDs.

Set the cell's `MODEL_PATH` if automatic discovery finds zero or multiple copies. A Drive web folder URL is not a mounted filesystem path. Shared folders may need a shortcut in My Drive. Startup can take several minutes, especially while loading weights from Drive.

**Status:** Application and launcher implemented. See [validation](docs/validation.md) for actual checks and remaining live Colab verification. Do not describe untested inference as a working demonstrated result.

## Workflow

- Upload photo, tree/block reference and observation; the evidence is saved first.
- AI supplies visible observations, tentative explanations, up to two follow-up questions, next checks and limitations.
- Answer questions to run a fresh analysis on the same saved image. Each successful output becomes a revision.
- Open a saved case, inspect its photo/history and mark it reviewed. A new successful analysis reopens it for review.
- Model failures retain the report and previous revisions with an explicit unavailable status. There are no canned AI responses.

## Documentation and presentation

- [Problem, assumptions and scope](docs/problem-and-scope.md)
- [Architecture and decisions](docs/architecture.md)
- [Seven-minute demo and Q&A](docs/demo-script.md)
- [Pitch content and claim ledger](docs/presentation.md)
- [AI journey / build log](docs/ai-journey.md)
- [Validation and live acceptance checks](docs/validation.md)
- [Sources, licensing and challenge disclosure](docs/disclosure.md)
- [Troubleshooting](docs/runbook.md)
- Draft slide: `output/presentation/hapus-scout-day1.pptx`; PDF: `output/pdf/hapus-scout-day1.pdf`.

## Layout

`app.py` holds the Gradio UI; `scout/` holds inference, schema validation, persistence and workflow; `knowledge/` holds a small source pack; `scripts/colab_bootstrap.py` starts the app; `notebooks/` holds the one-cell launcher. `tests/` uses isolated test doubles only.

## Development checks

```sh
python -m pip install Pillow gradio==5.49.1
python -m unittest discover -s tests -v
python app.py --ui-only
```

The last command is only for UI verification without GPU inference. Normal use is through Colab. For the full app, install `requirements.txt` in a CUDA-enabled environment and set `SCOUT_MODEL_PATH` and `SCOUT_DATA_DIR`. No paid AI API key is needed.

## Limits

Inspection support, not diagnosis or treatment. No agriculture-specific training or accuracy validation. Reference pack is static and intentionally small; citations are context, not proof of a diagnosis. English outputs; Marathi input is experimental. One shared, password-protected demo workspace; no worker/manager role separation. The temporary Gradio link and Colab session are not permanent hosting. Do not use confidential data.
