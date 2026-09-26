# Problem and scope

## Problem statement
Alphonso orchard workers need a simple way to turn a suspicious leaf or fruit observation into a useful inspection request, so farm managers know what to check and which evidence is missing.

## Users and job
Primary user: orchard worker with a smartphone. Secondary user: farm manager reviewing observations. The job is evidence collection and handoff, not remote diagnosis or automatic treatment.

## Hypotheses to validate
- Reports can lack consistent tree references, photos or symptom context.
- A photo-led follow-up workflow may improve report completeness.
- Managers may spend less time clarifying incomplete reports.

These are product hypotheses informed by the founder's domain choice, not interview findings or measured outcomes. No external human assistance was sought during this build.

## Day-1 assumptions
- Internet and a Colab GPU are available during the demonstration.
- The worker has permission to use the submitted photo.
- A human manager verifies the AI brief.
- Qwen can load from the existing Drive weights; live verification is required.
- A single shared team workspace is sufficient for the challenge.

## Included
Photo + text report, real vision inference, structured brief, up to two model-generated questions, follow-up re-analysis, saved case/photo/history, manager review marker, source context, visible failure states.

## Excluded
Confirmed disease diagnosis, chemical dosage, yield prediction, authenticity certification, offline inference, voice input, multi-tenant access, automated treatment and a full farm-management portal.

## Success evidence
Live unseen photo changes output; follow-up answer changes or refines the brief; unclear input triggers appropriate uncertainty; a saved case survives app restart; failed inference never yields fabricated success. Measure latency only from actual runs, and report model failure rates honestly.
