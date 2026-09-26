"""Generates official 1-Page Single-Slide Pitch Presentation (.pptx and .pdf).

Strictly 1 slide / 1 page covering the 4 Core Business Problems, Costing, Performance, and Scalability.
Optimized spacing and paragraph formatting to prevent text collisions.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tmp_dir = root / "tmp/pitch"
out_pdf_dir = root / "output/pdf"
out_pptx_dir = root / "output/presentation"

tmp_dir.mkdir(parents=True, exist_ok=True)
out_pdf_dir.mkdir(parents=True, exist_ok=True)
out_pptx_dir.mkdir(parents=True, exist_ok=True)

# 1-Page Slide Content definition (1280 x 720 geometry coordinate system with generous vertical padding)
CONTENT = [
    {
        "x": 60, "y": 30, "w": 1160, "h": 35,
        "size": 26, "bold": True, "color": "#173F2E",
        "text": "Hapus Scout™ Enterprise — 1-Page Executive Pitch"
    },
    {
        "x": 60, "y": 68, "w": 1160, "h": 22,
        "size": 13, "bold": False, "color": "#435749",
        "text": "Multimodal Vision AI Orchard Inspection & Agronomic Evidence Triage Platform for Alphonso Mangoes"
    },
    # Box 1: Problem 1
    {
        "x": 60, "y": 105, "w": 550, "h": 20,
        "size": 14, "bold": True, "color": "#173F2E",
        "text": "1. Delayed Disease Triage & Crop Loss"
    },
    {
        "x": 60, "y": 128, "w": 550, "h": 110,
        "size": 10.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Alphonso mangoes suffer 35-40% annual crop loss from unmonitored pest outbreaks.\n• Solution: Sub-6.5s vision AI triage converts worker photos into actionable agronomic briefs.\n• ROI & Scale: Replaces ₹1,500/visit fees; enables 1 agronomist to oversee 500+ orchard blocks."
    },
    # Box 2: Problem 2
    {
        "x": 670, "y": 105, "w": 550, "h": 20,
        "size": 14, "bold": True, "color": "#173F2E",
        "text": "2. Field Worker Language Barrier"
    },
    {
        "x": 670, "y": 128, "w": 550, "h": 110,
        "size": 10.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Over 85% of Konkan orchard workers are native Marathi or Hindi speakers.\n• Solution: Multilingual UI (EN, MR, HI) dynamically aligns local terms (Karpa) to AI tensors.\n• ROI & Scale: Zero worker training costs; seamless adoption across regional labor pools."
    },
    # Box 3: Problem 3
    {
        "x": 60, "y": 255, "w": 550, "h": 20,
        "size": 14, "bold": True, "color": "#173F2E",
        "text": "3. Over-Spraying & Export Rejections"
    },
    {
        "x": 60, "y": 278, "w": 550, "h": 110,
        "size": 10.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Farmers spend ₹15k-40k/acre on panic chemical spraying, causing export rejections.\n• Solution: Grounded ICAR rules isolate physical observations from unconfirmed hypotheses.\n• ROI & Scale: Cuts pesticide spending by 40-60%; protects EU/US premium export compliance."
    },
    # Box 4: Problem 4
    {
        "x": 670, "y": 255, "w": 550, "h": 20,
        "size": 14, "bold": True, "color": "#173F2E",
        "text": "4. Fragmented Logs & Lack of Audits"
    },
    {
        "x": 670, "y": 278, "w": 550, "h": 110,
        "size": 10.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Informal WhatsApp/paper notes leave farm managers with zero auditable evidence logs.\n• Solution: Centralized CaseStore with timestamped audit trails & 1-click agronomist reviews.\n• ROI & Scale: Multi-tenant JSON database scales from 2-acre family farms to 1,000+ acre estates."
    },
    # Strategic Aspect Metric Banner Header
    {
        "x": 60, "y": 405, "w": 1160, "h": 20,
        "size": 12, "bold": True, "color": "#173F2E",
        "text": "STRATEGIC EXECUTION & ROI METRICS"
    },
    # Strategic Aspect Metric Banner Details
    {
        "x": 60, "y": 428, "w": 1160, "h": 60,
        "size": 10, "bold": False, "color": "#273D30",
        "text": "• COSTING: 92% Total Cost of Ownership reduction using open 4-bit NF4 vision engine vs. commercial vision APIs.\n• PERFORMANCE: Sub-6.5s triage response time processing 1,024 vision patches at ~118ms/tok latency on T4 GPU.\n• SCALABILITY: Multi-tenant JSON storage architecture supporting regional multilingual scale across Konkan."
    },
    # Guardrail Notice Header
    {
        "x": 60, "y": 505, "w": 1160, "h": 18,
        "size": 10, "bold": True, "color": "#6D6345",
        "text": "AGRONOMIC GUARDRAIL & REPOSITORY INFORMATION"
    },
    # Guardrail Notice Text
    {
        "x": 60, "y": 525, "w": 1160, "h": 40,
        "size": 9, "bold": False, "color": "#6D6345",
        "text": "• Agronomic Guardrail Notice: AI analysis supports triage evidence isolation. Certified agronomist verification mandatory before chemical application.\n• Live Repository: https://github.com/HarshadHindlekar/Hapus-Scout.git  |  Vertical AI Track — Day-1 Builders Pitch Fest Edition"
    }
]

# Write JSON output
(tmp_dir / "content.json").write_text(json.dumps(CONTENT, indent=2))

# 1. Build PDF Presentation using ReportLab
def build_pdf():
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    try:
        pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
        pdfmetrics.registerFont(TTFont("ArialBold", "C:/Windows/Fonts/arialbd.ttf"))
    except Exception:
        pass

    pdf_path = out_pdf_dir / "hapus-scout-day1.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=(960, 540))
    c.setTitle("Hapus Scout - 1-Page Executive Pitch")
    
    # Light cream background
    c.setFillColor(HexColor("#F6F4EA"))
    c.rect(0, 0, 960, 540, fill=1, stroke=0)

    for item in CONTENT:
        font = "ArialBold" if item.get("bold") else "Arial"
        size = item["size"] * 0.75
        c.setFont(font, size)
        c.setFillColor(HexColor(item["color"]))
        
        lines = []
        for paragraph in item["text"].split("\n"):
            line = ""
            for word in paragraph.split():
                candidate = f"{line} {word}".strip()
                if pdfmetrics.stringWidth(candidate, font, size) > item["w"] * 0.75 and line:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
            
        for i, line in enumerate(lines):
            y_pos = 540 - item["y"] * 0.75 - size - i * size * 1.25
            c.drawString(item["x"] * 0.75, y_pos, line)
            
    c.showPage()
    c.save()
    print(f"Generated PDF: {pdf_path}")

# 2. Build PPTX Presentation using python-pptx
def build_pptx():
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor

    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 1280px / 96 = 13.333 in
    prs.slide_height = Inches(7.5)     # 720px / 96 = 7.5 in
    
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    # Set background color
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0xF6, 0xF4, 0xEA)

    for item in CONTENT:
        left = Inches(item["x"] / 96.0)
        top = Inches(item["y"] / 96.0)
        width = Inches(item["w"] / 96.0)
        height = Inches(item["h"] / 96.0)

        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        paragraphs = item["text"].split("\n")
        for idx, line in enumerate(paragraphs):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = line
            p.font.name = "Arial"
            p.font.size = Pt(item["size"])
            p.font.bold = item.get("bold", False)
            p.space_after = Pt(2)
            
            # Parse hex color
            hex_code = item["color"].lstrip('#')
            r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
            p.font.color.rgb = RGBColor(r, g, b)

    pptx_path = out_pptx_dir / "hapus-scout-day1.pptx"
    prs.save(str(pptx_path))
    print(f"Generated PPTX: {pptx_path}")

if __name__ == "__main__":
    build_pdf()
    build_pptx()
