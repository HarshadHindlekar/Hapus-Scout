# Validation record

## Automated checks
- Six workflow tests passed on 2026-09-26 using explicit test doubles, not real inference.
- Tests cover evidence preservation on outage/restart, follow-up context/history, review/reopen, failed retry retaining prior results, malformed/unrecognized reference rejection, path traversal and incomplete model weights.

## Additional checks completed
- Gradio 5.49.1 installed in an isolated environment; 36-component UI constructs successfully.
- Desktop browser inspection completed. Fixed low-contrast brief text in dark mode and rechecked visually. Missing-photo submission displays the expected error.
- HTTP smoke test passed: image upload, explicit AI-unavailable response, case/photo retrieval, human review and retry. A synthetic blank image was used, with no simulated AI analysis.
- Launcher cell syntax and Python compilation passed. Notebook has one executable cell with no stored outputs.
- One-slide PPTX passed package/layout/font checks and Artifact Tool re-import; rendered slide visually inspected. Companion one-page PDF rendered and visually inspected; text extracted successfully. Native PowerPoint was not used.
- Drive UI inspection located a Qwen3-VL configuration, both weight shards and processor files under the legacy folder named model-00001-of-00002.safetensors. This is file-presence evidence, not a GPU load test.

## Still to verify / record
- Mobile viewport and second-device access.
- Actual Drive model discovery and Colab T4 loading.
- A real permitted image and follow-up through Qwen.
- Blurry/non-plant image behavior, unsupported requests and invented certainty.
- Persistence after restarting the Colab app and access from a second device.

## Live acceptance table
| Scenario | Actual output / latency | Pass? |
|---|---|---|
| Clear permitted mango photo | Pending | Pending |
| Different photo changes observations | Pending | Pending |
| Follow-up changes or refines brief | Pending | Pending |
| Unclear/non-plant image requests better evidence | Pending | Pending |
| Prompt asking for a definitive diagnosis / dosage | Pending | Pending |
| Restart retains saved case | Pending live Drive check | Pending |

Do not infer model quality from mocked unit tests. Record failures as well as successes, and disclose latency based on actual runs only.
