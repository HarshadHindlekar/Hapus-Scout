"""Vector PDF companion generated from the same slide content and geometry."""
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

root = Path(__file__).resolve().parents[1]
out = root / "output/pdf"
out.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("ArialBold", "C:/Windows/Fonts/arialbd.ttf"))
c = canvas.Canvas(str(out / "hapus-scout-day1.pdf"), pagesize=(960, 540))
c.setTitle("Hapus Scout - Day 1 pitch draft")
c.setFillColor(HexColor("#F6F4EA")); c.rect(0, 0, 960, 540, fill=1, stroke=0)
for item in json.loads((root / "tmp/pitch/content.json").read_text()):
    font = "ArialBold" if item.get("bold") else "Arial"
    size = item["size"] * .75
    c.setFont(font, size); c.setFillColor(HexColor(item["color"]))
    lines = []
    for paragraph in item["text"].split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if pdfmetrics.stringWidth(candidate, font, size) > item["w"] * .75 and line:
                lines.append(line); line = word
            else:
                line = candidate
        lines.append(line)
    for i, line in enumerate(lines):
        c.drawString(item["x"] * .75, 540 - item["y"] * .75 - size - i * size * 1.2, line)
c.showPage(); c.save()
print(out / "hapus-scout-day1.pdf")
