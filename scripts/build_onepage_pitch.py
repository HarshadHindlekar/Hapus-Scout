"""Generates official 1-Page Single-Slide Pitch Presentation (.pptx and .pdf).

Strictly 1 slide / 1 page written in simple, plain, easy-to-understand English.
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

# 1-Page Slide Content definition in simple, plain English
CONTENT = [
    {
        "x": 60, "y": 30, "w": 1160, "h": 32,
        "size": 24, "bold": True, "color": "#173F2E",
        "text": "Hapus Scout™ Enterprise — Smart AI Inspection for Mango Farms"
    },
    {
        "x": 60, "y": 64, "w": 1160, "h": 20,
        "size": 12, "bold": False, "color": "#435749",
        "text": "Helping Alphonso mango farm workers spot crop diseases early and share instant photo reports with farm managers."
    },
    # Box 1: Problem 1
    {
        "x": 60, "y": 100, "w": 550, "h": 18,
        "size": 13, "bold": True, "color": "#173F2E",
        "text": "1. Slow Disease Detection Causes 40% Crop Loss"
    },
    {
        "x": 60, "y": 120, "w": 550, "h": 85,
        "size": 9.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Alphonso farmers lose nearly 40% of their mangoes each year because diseases spread unseen.\n• Solution: Workers upload a photo and get a clear AI checkup report in less than 7 seconds.\n• Impact: Saves ₹1,500 per expert visit; allows 1 manager to easily look after 500+ orchard blocks."
    },
    # Box 2: Problem 2
    {
        "x": 670, "y": 100, "w": 550, "h": 18,
        "size": 13, "bold": True, "color": "#173F2E",
        "text": "2. Language Barrier for Farm Workers"
    },
    {
        "x": 670, "y": 120, "w": 550, "h": 85,
        "size": 9.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Over 85% of workers speak only Marathi or Hindi and cannot use complicated English apps.\n• Solution: Simple 1-click switch between English, Marathi (मराठी), and Hindi (हिंदी).\n• Impact: Workers can report symptoms in their own native language with zero training needed."
    },
    # Box 3: Problem 3
    {
        "x": 60, "y": 230, "w": 550, "h": 18,
        "size": 13, "bold": True, "color": "#173F2E",
        "text": "3. Wasting Money on Wrong Pesticide Sprays"
    },
    {
        "x": 60, "y": 250, "w": 550, "h": 85,
        "size": 9.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Scared farmers spend ₹15,000 to ₹40,000 per acre buying wrong sprays, harming crop exports.\n• Solution: AI follows official government farming rules (ICAR) and separates facts from guesses.\n• Impact: Cuts pesticide costs by 40% to 60% and keeps mangoes safe for international export."
    },
    # Box 4: Problem 4
    {
        "x": 670, "y": 230, "w": 550, "h": 18,
        "size": 13, "bold": True, "color": "#173F2E",
        "text": "4. Lost Paper Records & Messy Chat Messages"
    },
    {
        "x": 670, "y": 250, "w": 550, "h": 85,
        "size": 9.5, "bold": False, "color": "#273D30",
        "text": "• Problem: Farm notes get lost on WhatsApp or paper, giving managers no real inspection history.\n• Solution: Automatic digital library stores every photo, symptom report, and manager review.\n• Impact: Works for small 2-acre family farms as well as large 1,000-acre commercial estates."
    },
    # Strategic Aspect Metric Banner Header
    {
        "x": 60, "y": 360, "w": 1160, "h": 18,
        "size": 11, "bold": True, "color": "#173F2E",
        "text": "KEY ADVANTAGES: COST, SPEED & SCALABILITY"
    },
    # Strategic Aspect Metric Banner Details
    {
        "x": 60, "y": 380, "w": 1160, "h": 75,
        "size": 9.5, "bold": False, "color": "#273D30",
        "text": "• LOW COST: 90%+ cheaper to run by using smart lightweight local AI models on low-cost devices.\n• FAST SPEED: Under 7 seconds per photo checkup so workers get instant answers right on the field.\n• EASY TO SCALE: Native Marathi/Hindi support allows rapid deployment across all Konkan mango farms."
    },
    # Guardrail Notice Header
    {
        "x": 60, "y": 485, "w": 1160, "h": 16,
        "size": 9.5, "bold": True, "color": "#6D6345",
        "text": "SAFETY NOTICE & PROJECT LINK"
    },
    # Guardrail Notice Text
    {
        "x": 60, "y": 503, "w": 1160, "h": 40,
        "size": 8.5, "bold": False, "color": "#6D6345",
        "text": "• Farm Safety Notice: AI assists initial checking only. Certified farming experts must verify before chemical spraying.\n• Open Code Repository: https://github.com/HarshadHindlekar/Hapus-Scout.git"
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
    c.setTitle("Hapus Scout Enterprise Pitch")
    
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
