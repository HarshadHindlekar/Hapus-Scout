# One-slide pitch source

Title: Hapus Scout
Subtitle: Orchard inspection support for Alphonso mango teams

Problem hypothesis: Workers need a consistent way to report suspicious leaf or fruit symptoms; managers need enough evidence to decide what to inspect.

Workflow: Photo + worker note -> AI observations + questions -> manager inspection brief.

AI contribution: Qwen3-VL interprets the image, asks contextual follow-up questions and revises the brief when evidence changes.

Technical choices: One Colab runtime; Gradio interface; Qwen weights and cases in Drive.

Boundary: Inspection support, not confirmed diagnosis. Internet and a running GPU session are assumed.

Next: Agronomist evaluation, Marathi/voice usability and team permissions.

## Claim ledger
| Claim | Status / evidence |
|---|---|
| One repository and single-cell launcher | Implemented; notebook syntax check required |
| Saved case, history and failure preservation | Covered by automated workflow tests |
| Real Qwen integration | Implemented; live Drive/GPU acceptance pending |
| Dynamic follow-up | Connected to model call; live quality acceptance pending |
| Accurate mango diagnosis | Not claimed or validated |
| Reduced crop losses / proven time savings | Not measured; do not claim |
| Marathi support | Experimental input, English output; no evaluated multilingual claim |

The generated slide is a draft until the live acceptance checks are complete. Refresh the claim ledger after each demonstration; do not replace pending checks with assumptions.
