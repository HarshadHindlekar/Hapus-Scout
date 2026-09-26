# Hapus Scout AI journey

## 2026-09-26 — First implementation

Decision: narrow the Day-1 vertical AI problem to orchard inspection evidence and manager handoff for Alphonso mango teams.

Architecture correction from founder feedback: keep UI and vision model together in Colab, with one repository and one launcher. Avoid a local/Vercel frontend and manual Cloudflare gateway synchronization.

Implemented: photo/text intake, persistent cases, Qwen integration, strict output schema, evidence-driven follow-up, history, manager review and explicit inference failure handling. Existing Drive weights are reused; application code is newly authored.

Documentation: problem/scope, architecture decisions, runbook, source/reuse disclosure, validation checklist, seven-minute demo script and one-slide pitch source. Draft presentation and PDF accompany these documents.

Verification: six workflow tests passed on the first run, including inference outages, follow-up history, invented references, missing model shards and path validation. GPU model loading and end-to-end Colab inference are not yet verified. UI and artifact checks are recorded in validation.md as completed.

Open risks: model may hallucinate, produce invalid JSON or mishandle Marathi; free Colab availability and share links are temporary. No diagnostic accuracy or commercial outcome claims are justified yet.

Follow-through: browser and HTTP smoke checks passed for the UI and failure/persistence workflow. Fixed brief text contrast in dark mode. Draft PPTX passed structure/layout checks and visual review; its PDF companion passed rendering and text checks. Located the actual Drive weights in a legacy folder named after the first shard and added that location as the launcher's first candidate. Live GPU inference remains pending.
