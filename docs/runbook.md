# Colab runbook

## Normal start
Open the repository notebook, choose a GPU, run its single cell, approve Drive mount, wait for model load, then open the Gradio URL using the printed temporary login. Select the Google account that owns the model or has a My Drive shortcut to it.

The launcher first checks the existing layout `MyDrive/Hapus More AI/models/model-00001-of-00002.safetensors`. Despite the suffix, this is a folder containing both weight shards and config.json. If absent, automatic discovery searches My Drive. The similarly named Qwen3-VL-4B-Instruct folder was empty in the inspected Drive view.

## Troubleshooting

Startup now forwards child-process stdout and stderr into the notebook. It prints dependency, file-validation, GPU-loading and interface-launch stages, with a waiting message after 30 seconds without child output. A waiting message means the process is alive, not that model loading is making progress. The cell continues running while the app serves requests; look for the Gradio URL rather than waiting for execution to finish.

If an older launcher stops visibly at "Model found", stop that cell once and rerun the updated launcher in the same runtime. Do not delete the runtime: downloaded temporary weights can be reused. Existing older child processes may survive interruption; if a rerun reports GPU memory or port conflicts, inspect and stop the old Scout process before retrying.

If the minimal `drive.mount('/content/drive')` command raises `credential propagation was unsuccessful`, authentication is failing before Scout examines model files. A missing model folder would be a later, different error. Do not infer model ownership or the exact failed OAuth scope from this message alone.

To keep building, reopen the latest launcher and set `USE_DRIVE = False`. It downloads the public model through Hugging Face to temporary Colab disk, without mounting Drive. Allow time for the multi-gigabyte download. No cases persist after runtime deletion. This is an explicit alternate mode, not an automatic fallback or a fix for Google's authentication problem.
| Symptom | Action |
|---|---|
| No CUDA GPU | Select a GPU runtime; if Colab has no quota, the GPU demo cannot run there |
| Zero model folders found | Set MODEL_PATH to the mounted directory containing config.json and weights; URLs are not paths |
| Multiple models found | Choose the correct Qwen3-VL-4B-Instruct folder explicitly |
| Missing shard | Restore the full download; the launcher refuses partial weights |
| Missing processor assets | Loader tries the official model processor; network access is required |
| Out of GPU memory | Stop other models, restart the runtime and launch Scout alone |
| Invalid AI response | Report stays saved; retry. Do not represent it as successful analysis |
| Share link unavailable | Check the cell is running; restart creates a new temporary link |
| Repo authentication required | Public repository launcher assumes readable GitHub code; a private repo needs authenticated cloning, never a token pasted into tracked notebook code |

## Persistence
Cases live under `/content/drive/MyDrive/HapusScout/cases`. Each folder contains a metadata-free photo and case.json with report/revisions. Use only demonstration data. All users of the shared demo login can view these cases. The model folder is read-only to the app.

## Shutdown / next session
Stop the cell when the demo is over. Re-run to restore model and cases. The notebook does not bypass Colab runtime limits, keep sessions artificially alive or start paid resources.
