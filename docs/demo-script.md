# Seven-minute demo and three-minute Q&A

## Before judging
- If using `USE_DRIVE = False`, disclose that weights were downloaded from the public model repository and cases use temporary Colab storage. The draft slide describes the default Drive mode; explain this operational difference during the demo.
- Complete docs/validation.md live checks; load the model before the slot.
- Use your own or explicitly permitted photos; keep a rights note for each.
- Choose one clear plant photo, a different photo and one unclear/non-plant photo. Do not predetermine their AI outputs.
- Keep the notebook running and the login ready. Confirm the demo link opens on a second browser/device.
- Record the submission commit and deadline. Do not claim post-deadline changes.

## 0:00-0:50 — One slide
"We chose a narrow reporting problem for Alphonso orchard teams: turning a suspicious leaf or fruit into an inspection request with enough evidence. Our hypothesis is that guided follow-up reduces missing context. Hapus Scout helps the worker document the issue and gives the manager a brief to verify."

## 0:50-2:30 — New report
Upload a permitted image, use a fictional tree ID, describe what you see. Submit live. Explain that the image and text go to Qwen running in the same Colab runtime as the interface. Report real elapsed time; avoid claiming a target latency as measured performance.

## 2:30-4:00 — Follow-up
Read the actual generated questions. Answer with explicitly hypothetical demo context. Re-analyze. Point to what changed and what remained uncertain. If the model fails, show the preserved report and honest retry status.

## 4:00-5:10 — Manager handoff
Open the case list, photo, latest brief and revision history. Mark the case reviewed. Explain that this records review, not confirmed diagnosis.

## 5:10-6:15 — Different / insufficient evidence
Try the other photo or an unclear input. Discuss the actual result. If the model speculates or misreads the photo, acknowledge the limitation rather than hiding it.

## 6:15-7:00 — Choices and next steps
"Gradio, model and workflow share one Colab runtime. Drive keeps weights and case records. Next we would evaluate reports with an agronomist, improve Marathi input, add voice and proper team permissions. We have not demonstrated crop-loss reduction or diagnostic accuracy."

## Q&A preparation
- Why AI? The photo and free-text evidence vary; the model generates image observations and contextual questions dynamically.
- Why not a chatbot? The product produces a persistent inspection case with a photo, questions, revisions and a manager handoff.
- What was trained? Nothing. We use existing Qwen weights and a small static source pack.
- What happens offline? Live AI is unavailable. Offline capture/sync is future work.
- What is reused? Existing open model weights and public packages. Application code is newly written for this implementation; verify dates against the official challenge window.
- What is the business value? More complete inspection requests is a hypothesis to measure, not a proven ROI claim.
