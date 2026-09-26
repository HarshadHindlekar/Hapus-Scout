# Hapus Scout workflow

- Keep UI, inference, launcher and documentation in this repository.
- Run the product in Colab; do not introduce Vercel or a separate frontend deployment.
- Keep model weights, case images, credentials and runtime files out of Git.
- Never fabricate AI outputs or silently replace inference with rules.
- Preserve the distinction between observed evidence, hypotheses and human review.
- After product changes update docs/ai-journey.md, docs/validation.md and relevant architecture/demo docs.
- Keep the one-slide pitch and PDF aligned with actual implementation and verified capabilities.
- Use one writer per file scope. No background coordination daemon is needed.
