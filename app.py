"""Run in Colab through notebooks/launch_colab.ipynb."""
import argparse
import html
import os
import secrets
import inspect
import gradio as gr
from scout.inspection import REFERENCES
from scout.model import VisionModel
from scout.service import ScoutService
from scout.storage import CaseStore

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* Global Reset & Background */
html, body {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 40%, #08281e 100%) !important;
    min-height: 100vh !important;
    color: #0f172a !important;
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    margin: 0;
    padding: 0;
}

/* GRADIO LOGIN PAGE OVERRIDES */
form[action="/login"], .login, div:has(> form[action="/login"]) {
    background: rgba(255, 255, 255, 0.96) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35), 0 0 30px rgba(16, 185, 129, 0.15) !important;
    border-radius: 24px !important;
    max-width: 440px !important;
    margin: 60px auto !important;
    padding: 40px 36px !important;
    box-sizing: border-box !important;
    text-align: center !important;
    position: relative !important;
}

form[action="/login"]::before {
    content: "🥭 HAPUS SCOUT™ ENTERPRISE";
    display: block;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #064e3b;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
}

form[action="/login"]::after {
    content: "Alphonso Orchard Inspection Platform · Sign in to your workspace";
    display: block;
    font-size: 13px;
    color: #64748b;
    margin-bottom: 24px;
}

form[action="/login"] label {
    display: block !important;
    text-align: left !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #334155 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-top: 14px !important;
    margin-bottom: 6px !important;
}

form[action="/login"] input[type="text"],
form[action="/login"] input[type="password"] {
    width: 100% !important;
    padding: 14px 16px !important;
    font-size: 14px !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

form[action="/login"] input[type="text"]:focus,
form[action="/login"] input[type="password"]:focus {
    border-color: #10b981 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15) !important;
    outline: none !important;
}

form[action="/login"] button, form[action="/login"] input[type="submit"] {
    width: 100% !important;
    margin-top: 24px !important;
    padding: 14px 20px !important;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
    transition: all 0.2s ease !important;
}

form[action="/login"] button:hover, form[action="/login"] input[type="submit"]:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45) !important;
}

/* MAIN APP CONTAINER OVERRIDES */
.gradio-container {
    width: 100% !important;
    max-width: 1320px !important;
    margin: 0 auto !important;
    padding: clamp(16px, 2vw, 32px) !important;
    box-sizing: border-box !important;
}

.gradio-container .main {
    background: #f4f7f4 !important;
    border-radius: 24px !important;
    padding: 24px !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25) !important;
}

.gradio-container .app, .gradio-container .html-container {
    padding: 0 !important;
}

/* Header & Hero Branding */
#hero {
    background: linear-gradient(135deg, #04392b 0%, #022018 100%);
    color: #ffffff;
    padding: 28px 36px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(4, 57, 43, 0.3);
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 18px;
}

.brand-icon {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #ffffff;
    border-radius: 16px;
    display: grid;
    place-items: center;
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.brand-title h1 {
    color: #ffffff !important;
    font-size: 30px !important;
    font-weight: 800 !important;
    letter-spacing: -0.6px;
    margin: 0 !important;
    line-height: 1.1;
}

.brand-title .badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #6ee7b7;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.system-status-pills {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.status-pill {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 600;
    padding: 7px 16px;
    border-radius: 30px;
    display: flex;
    align-items: center;
    gap: 8px;
    backdrop-filter: blur(10px);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 10px #10b981;
}

/* Metric Strip */
.metrics-strip {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}

.metric-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.metric-value {
    font-size: 18px;
    font-weight: 800;
    color: #064e3b;
}

.metric-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Preset Scenario Bar */
.preset-bar-wrapper {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.preset-title {
    font-size: 12px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Cards and Panels */
#report-panel, #brief-panel, #library-panel, #case-panel {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 26px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
}

.section-head {
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid #f1f5f9;
}

.section-head h3 {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin: 0 0 6px !important;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.3px;
}

.section-head p {
    font-size: 13px !important;
    color: #64748b !important;
    margin: 0 !important;
}

/* Custom Tabs Styling */
.tab-nav {
    border-bottom: 2px solid #e2e8f0 !important;
    gap: 28px !important;
    margin-bottom: 24px !important;
}

.tab-nav button {
    padding: 14px 10px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #64748b !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.2s ease !important;
}

.tab-nav button.selected {
    color: #059669 !important;
    border-bottom: 3px solid #059669 !important;
    font-weight: 700 !important;
}

/* Image Upload Dropzone */
#photo-input {
    border: 2px dashed #cbd5e1 !important;
    background: #f8fafc !important;
    border-radius: 16px !important;
    transition: border-color 0.2s ease;
}

#photo-input:hover {
    border-color: #10b981 !important;
}

/* Storage Alert */
#storage-note {
    background: #fffbe6;
    border: 1px solid #ffe58f;
    padding: 14px 20px !important;
    border-radius: 14px;
    color: #873800;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Rendered Brief Custom HTML */
.brief-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 4px;
    color: #0f172a;
    line-height: 1.6;
}

.brief-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    padding-bottom: 16px;
    margin-bottom: 16px;
    border-bottom: 1px solid #f1f5f9;
}

.case-id-tag {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #64748b;
    background: #f1f5f9;
    padding: 4px 10px;
    border-radius: 6px;
    text-transform: uppercase;
}

.status-badge-open {
    font-size: 12px;
    font-weight: 700;
    color: #d97706;
    background: #fef3c7;
    border: 1px solid #fde68a;
    padding: 4px 12px;
    border-radius: 20px;
}

.status-badge-reviewed {
    font-size: 12px;
    font-weight: 700;
    color: #059669;
    background: #d1fae5;
    border: 1px solid #a7f3d0;
    padding: 4px 12px;
    border-radius: 20px;
}

.quality-badge-usable {
    font-size: 12px;
    font-weight: 600;
    color: #047857;
    background: #ecfdf5;
    padding: 4px 10px;
    border-radius: 6px;
}

.quality-badge-unclear {
    font-size: 12px;
    font-weight: 600;
    color: #b45309;
    background: #fffbe6;
    padding: 4px 10px;
    border-radius: 6px;
}

.brief-location {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.worker-obs-box {
    background: #f8fafc;
    border-left: 4px solid #059669;
    padding: 12px 16px;
    border-radius: 0 10px 10px 0;
    margin-bottom: 18px;
    font-size: 14px;
    color: #334155;
}

.exec-summary-box {
    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
    border: 1px solid #a7f3d0;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    color: #065f46;
    font-size: 15px;
    font-weight: 500;
}

.brief-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 20px;
}

.brief-section-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
}

.brief-section-title {
    font-size: 14px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.brief-section-card ul {
    margin: 0;
    padding-left: 20px;
}

.brief-section-card li {
    margin-bottom: 6px;
    font-size: 14px;
    color: #334155;
}

.badge-unconfirmed {
    font-size: 10px;
    font-weight: 700;
    background: #fef3c7;
    color: #b45309;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
}

.citation-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    color: #0f172a !important;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-decoration: none !important;
    margin-right: 8px;
    margin-bottom: 8px;
    transition: background 0.2s ease;
}

.citation-pill:hover {
    background: #e2e8f0;
}

.safety-disclaimer {
    background: #fffbe6;
    border: 1px solid #ffe58f;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 12px;
    color: #873800;
    line-height: 1.5;
    margin-top: 16px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
}

/* Empty Brief Placeholder */
.empty-brief-container {
    min-height: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 40px 24px;
    border: 2px dashed #e2e8f0;
    border-radius: 16px;
    background: #fafcfb;
}

.empty-brief-icon {
    width: 64px;
    height: 64px;
    background: #ecfdf5;
    color: #059669;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 28px;
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.1);
}

.empty-brief-container h3 {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin: 0 0 8px 0 !important;
}

.empty-brief-container p {
    font-size: 13px !important;
    color: #64748b !important;
    max-width: 340px;
    margin: 0 !important;
    line-height: 1.6;
}

.help-line {
    font-size: 12px !important;
    color: #94a3b8 !important;
    margin-top: 8px !important;
}

@media (max-width: 640px) {
    .gradio-container { padding: 12px !important; }
    #hero { padding: 20px 20px; }
    .brand-title h1 { font-size: 24px !important; }
    .metrics-strip { flex-direction: column; align-items: flex-start; gap: 12px; }
    #report-panel, #brief-panel, #library-panel, #case-panel { padding: 18px !important; }
}
"""


def scout_theme():
    theme = gr.themes.Base(primary_hue="emerald", neutral_hue="slate", font=["Plus Jakarta Sans", "Inter", "sans-serif"])
    values = dict(
        body_background_fill="#04392b",
        body_text_color="#0f172a",
        body_text_color_subdued="#64748b",
        background_fill_primary="#ffffff",
        background_fill_secondary="#f8fafc",
        border_color_primary="#e2e8f0",
        block_background_fill="#ffffff",
        block_border_width="1px",
        block_border_color="#e2e8f0",
        block_label_background_fill="transparent",
        block_label_text_color="#334155",
        block_title_text_color="#0f172a",
        block_title_background_fill="transparent",
        block_label_text_size="13px",
        block_label_text_weight="600",
        block_label_padding="4px 0",
        block_shadow="0 2px 8px rgba(0,0,0,0.02)",
        input_background_fill="#f8fafc",
        input_border_color="#cbd5e1",
        input_border_color_focus="#059669",
        input_shadow="none",
        input_text_size="14px",
        input_radius="10px",
        input_placeholder_color="#94a3b8",
        button_primary_background_fill="#059669",
        button_primary_background_fill_hover="#047857",
        button_primary_text_color="#ffffff",
        button_primary_border_color="#059669",
        button_secondary_background_fill="#f1f5f9",
        button_secondary_background_fill_hover="#e2e8f0",
        button_secondary_text_color="#1e293b",
        button_secondary_border_color="#cbd5e1",
        button_large_radius="10px",
        button_large_text_size="14px",
        checkbox_label_background_fill="#ffffff",
        checkbox_label_text_color="#334155",
        checkbox_label_background_fill_selected="#ecfdf5",
        checkbox_label_text_color_selected="#047857",
        checkbox_label_border_color="#e2e8f0",
        checkbox_label_border_color_selected="#059669",
        color_accent_soft="#ecfdf5",
        panel_background_fill="#ffffff",
        block_padding="12px",
        layout_gap="20px",
        block_radius="12px",
    )
    parameters = inspect.signature(theme.set).parameters
    for name, value in list(values.items()):
        if name + "_dark" in parameters:
            values[name + "_dark"] = value
    return theme.set(**values)


def empty_brief(title, description):
    return (
        f'<div class="empty-brief-container">'
        f'<div class="empty-brief-icon">🔍</div>'
        f'<h3>{html.escape(title)}</h3>'
        f'<p>{html.escape(description)}</p>'
        f'</div>'
    )


def render(case):
    esc = lambda value: html.escape(str(value))
    status_class = "status-badge-reviewed" if case["status"] == "reviewed" else "status-badge-open"
    
    parts = [
        f'<div class="brief-card">',
        f'<div class="brief-header">',
        f'<div><span class="case-id-tag">CASE REF: {esc(case["id"][:8])}</span></div>',
        f'<div><span class="{status_class}">● {esc(case["status"].upper())}</span></div>',
        f'</div>',
        f'<h2 class="brief-location">📍 {esc(case["report"]["location"])} <span style="font-size:14px; font-weight:500; color:#64748b;">({esc(case["report"]["part"])})</span></h2>',
        f'<div class="worker-obs-box"><b>Field Observation:</b> "{esc(case["report"]["observation"])}"</div>'
    ]

    if case["analysis_status"] == "pending":
        parts.append('<div class="exec-summary-box" style="background:#fffbe6; border-color:#ffe58f; color:#873800;">⏳ Report registered. Qwen3-VL Vision AI is examining image evidence. Keep session active...</div>')
    elif case["analysis_status"] != "ready":
        parts.append('<div class="exec-summary-box" style="background:#fef2f2; border-color:#fecaca; color:#991b1b;">⚠️ Multimodal AI inference pending or unavailable. Photo and worker record are securely preserved. Retry when model is active.</div>')

    if case["revisions"]:
        revision = case["revisions"][-1]
        result = revision["analysis"]
        quality_class = "quality-badge-usable" if result["image_quality"] == "usable" else "quality-badge-unclear"
        
        parts.append('<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">')
        parts.append(f'<span class="{quality_class}">📷 Evidence Quality: {esc(result["image_quality"].upper())}</span>')
        parts.append(f'<span style="font-size:11px; color:#94a3b8;">{esc(revision["model"])} · Latency: {esc(revision["seconds"])}s · Rev #{len(case["revisions"])}</span>')
        parts.append('</div>')

        parts.append(f'<div class="exec-summary-box"><b>Executive Summary:</b><br>{esc(result["summary"])}</div>')

        parts.append('<div class="brief-grid">')

        # Visible Observations
        obs_items = "".join(f'<li>{esc(item)}</li>' for item in result["observations"]) if result["observations"] else "<li>No specific visual anomaly isolated.</li>"
        parts.append(
            f'<div class="brief-section-card" style="border-left: 4px solid #10b981;">'
            f'<div class="brief-section-title"><span>🔍</span> Visible Physical Evidence</div>'
            f'<ul>{obs_items}</ul>'
            f'</div>'
        )

        # Possible Explanations (Hypotheses)
        exp_items = "".join(f'<li>{esc(item)}</li>' for item in result["possible_explanations"]) if result["possible_explanations"] else "<li>No explanations generated (insufficient evidence).</li>"
        parts.append(
            f'<div class="brief-section-card" style="border-left: 4px solid #f59e0b;">'
            f'<div class="brief-section-title"><span>💡</span> Possible Hypotheses <span class="badge-unconfirmed">Unconfirmed</span></div>'
            f'<ul>{exp_items}</ul>'
            f'</div>'
        )

        # Questions for Worker
        q_items = "".join(f'<li>{esc(item)}</li>' for item in result["questions"]) if result["questions"] else "<li>No additional questions required.</li>"
        parts.append(
            f'<div class="brief-section-card" style="border-left: 4px solid #3b82f6;">'
            f'<div class="brief-section-title"><span>❓</span> Questions for Field Worker</div>'
            f'<ul>{q_items}</ul>'
            f'</div>'
        )

        # Next Checks
        check_items = "".join(f'<li>{esc(item)}</li>' for item in result["next_checks"]) if result["next_checks"] else "<li>Standard agronomic monitoring recommended.</li>"
        parts.append(
            f'<div class="brief-section-card" style="border-left: 4px solid #14b8a6;">'
            f'<div class="brief-section-title"><span>📋</span> Next Evidence to Collect</div>'
            f'<ul>{check_items}</ul>'
            f'</div>'
        )

        # Uncertainties & Limitations
        lim_items = "".join(f'<li>{esc(item)}</li>' for item in result["limitations"]) if result["limitations"] else "<li>Standard vision model constraints apply.</li>"
        parts.append(
            f'<div class="brief-section-card" style="border-left: 4px solid #64748b;">'
            f'<div class="brief-section-title"><span>🛡️</span> Technical Uncertainties & Constraints</div>'
            f'<ul>{lim_items}</ul>'
            f'</div>'
        )

        parts.append('</div>') # End grid

        # Reference Context Citations
        sources = [r for r in REFERENCES if r["id"] in result["reference_ids"]]
        if sources:
            parts.append('<div style="margin-top:16px;"><div class="brief-section-title" style="font-size:13px; color:#475569;">📚 Grounded Agricultural References</div><div>')
            for r in sources:
                parts.append(f'<a href="{esc(r["url"])}" target="_blank" rel="noopener" class="citation-pill">📄 {esc(r["title"])} ↗</a>')
            parts.append('</div></div>')

    parts.append(
        '<div class="safety-disclaimer">'
        '<span>🛡️</span>'
        '<div><b>Agronomic Protocol Guardrail:</b> This AI brief is for structured field inspection support. '
        'All hypotheses must be verified by a certified orchard manager or agronomist. No chemical prescriptions or fruit authenticity guarantees provided.</div>'
        '</div>'
    )
    parts.append('</div>')
    return "".join(parts)


def build_app(service):
    def choices():
        return [(f'📍 {c["report"]["location"]} · [{c["status"].upper()}] · #{c["id"][:8]}', c["id"]) for c in service.store.list()]

    def submit(image, location, part, observation):
        try:
            case = service.submit(image, location, part, observation)
        except ValueError as exc:
            raise gr.Error(str(exc)) from exc
        yield case["id"], render(case), "", gr.update(choices=choices())
        case = service.analyze(case["id"])
        yield case["id"], render(case), "", gr.update(choices=choices())

    def follow(case_id, answer):
        if not case_id:
            raise gr.Error("Create or open a case first.")
        try:
            case = service.analyze(case_id, answer)
        except ValueError as exc:
            raise gr.Error(str(exc)) from exc
        return render(case), gr.update(choices=choices())

    def open_case(case_id):
        if not case_id:
            raise gr.Error("Choose a saved case first.")
        case = service.store.get(case_id)
        return case_id, render(case), service.store.photo(case_id), case

    def review(case_id):
        if not case_id:
            raise gr.Error("Open a case first.")
        case = service.store.reviewed(case_id)
        return render(case), case, gr.update(choices=choices())

    # Demo Presets
    def set_preset_1():
        return "Block A / Row 4 / Tree 18", "Leaf", "Dark irregular brown spots with yellow margins on upper leaf canopy. Noticed 3 days after heavy rainfall."

    def set_preset_2():
        return "Block C / Tree 05 (Fruit Zone)", "Fruit", "Mature Alphonso mango showing soft puncture mark near stem end. 2 fallen fruits detected under canopy."

    def set_preset_3():
        return "Block B / Tree 12", "Leaf", "Low light canopy photo. Leaves appear pale green from a distance."

    with gr.Blocks(title="Hapus Scout Enterprise", theme=scout_theme(), css=CSS) as demo:
        # Header
        gr.HTML(
            '<header id="hero">'
            '<div class="brand-wrapper">'
            '<div class="brand-icon">'
            '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.12 2 9a7 7 0 0 1-10 9z"></path><path d="M11 20v-8.5"></path></svg>'
            '</div>'
            '<div class="brand-title">'
            '<span class="badge">Hapus & More AI Platform</span>'
            '<h1>Hapus Scout™ Enterprise</h1>'
            '</div>'
            '</div>'
            '<div class="system-status-pills">'
            '<div class="status-pill"><span class="status-dot"></span>Qwen3-VL Vision Model</div>'
            '<div class="status-pill">🥭 Alphonso Orchard Module</div>'
            '<div class="status-pill" style="border-color:#f59e0b; color:#fbbf24;">🏆 Day-1 Pitch Fest</div>'
            '</div>'
            '</header>'
        )

        # Metric & Workflow Bar
        gr.HTML(
            '<div class="metrics-strip">'
            '<div class="metric-item"><span class="metric-value">12</span><span class="metric-label">Orchard Blocks</span></div>'
            '<div style="color:#cbd5e1;">│</div>'
            '<div class="metric-item"><span class="metric-value">Qwen3-VL</span><span class="metric-label">Vision Model (4-Bit)</span></div>'
            '<div style="color:#cbd5e1;">│</div>'
            '<div class="metric-item"><span class="metric-value">0 Prescriptions</span><span class="metric-label">Safety Enforced</span></div>'
            '<div style="color:#cbd5e1;">│</div>'
            '<div class="metric-item"><span class="metric-value">ICAR Grounded</span><span class="metric-label">Agronomic Rules</span></div>'
            '</div>'
        )

        if os.environ.get("SCOUT_STORAGE_MODE") == "temporary":
            gr.HTML(
                '<div id="storage-note">'
                '<span>⚡</span> <b>Session-Only Cloud Sandbox</b> · Inspection reports are preserved for this active session. Permanent Drive sync disabled.'
                '</div>'
            )

        with gr.Tab("⚡ New Inspection"):
            current = gr.State("")

            # Quick Presets Bar
            gr.HTML(
                '<div class="preset-bar-wrapper">'
                '<div class="preset-title">⚡ Quick Demo Presets (Click to auto-fill sample orchard issues):</div>'
                '</div>'
            )
            with gr.Row():
                preset1_btn = gr.Button("🍃 Preset 1: Anthracnose Leaf Lesions", size="sm", variant="secondary")
                preset2_btn = gr.Button("🥭 Preset 2: Fruit Fly Soft Spot", size="sm", variant="secondary")
                preset3_btn = gr.Button("🌫️ Preset 3: Low-Light Blurry Canopy", size="sm", variant="secondary")

            with gr.Row():
                with gr.Column(scale=4, min_width=320, elem_id="report-panel", variant="panel"):
                    gr.HTML(
                        '<div class="section-head">'
                        '<h3>📷 Field Evidence Capture</h3>'
                        '<p>Upload a high-resolution leaf or fruit photo with orchard block details.</p>'
                        '</div>'
                    )
                    photo = gr.Image(type="pil", label="Leaf or Fruit Evidence Photo", sources=["upload", "webcam"], height=240, elem_id="photo-input")
                    location = gr.Textbox(label="Orchard Block / Tree Tag", placeholder="e.g. Block A / Tree 18", max_length=160)
                    part = gr.Radio(["Leaf", "Fruit", "Other / uncertain"], value="Leaf", label="Target Inspection Subject")
                    observation = gr.Textbox(label="Worker Observations & Symptoms", placeholder="Describe visual symptoms, onset time, or nearby trees...", lines=3, max_length=2000)
                    send = gr.Button("⚡ Analyze Inspection with Vision AI →", variant="primary", size="lg")
                    gr.HTML('<p class="help-line">🔒 Evidence processed securely via Qwen3-VL on Colab runtime.</p>')

                with gr.Column(scale=6, min_width=340, elem_id="brief-panel", variant="panel"):
                    gr.HTML(
                        '<div class="section-head">'
                        '<h3>📊 AI Agronomic Inspection Brief</h3>'
                        '<p>Multimodal vision analysis, evidence triage, and open questions.</p>'
                        '</div>'
                    )
                    brief = gr.HTML(empty_brief("Inspection Brief Ready for Input", "Upload a leaf or fruit photo, fill field notes or pick a demo scenario, then click Analyze Inspection."))
                    
                    with gr.Accordion("💬 Answer AI Follow-Up Questions / Add Evidence", open=False):
                        answer = gr.Textbox(label="Worker Responses or Additional Observations", placeholder="Enter answers to Scout's follow-up questions...", lines=2, max_length=2000)
                        update = gr.Button("🔄 Re-evaluate Brief with Follow-Up Data", variant="secondary")
                    
                    gr.HTML('<p class="help-line">💡 Grounded with ICAR-CISH & NHB Mango Cultivation Standards.</p>')

        with gr.Tab("📁 Orchard Case Library"):
            gr.HTML(
                '<div class="section-head">'
                '<h3>📁 Central Orchard Case Management</h3>'
                '<p>Audit submitted field reports, track inspection statuses, and confirm agronomist reviews.</p>'
                '</div>'
            )
            manager_id = gr.State("")
            with gr.Row():
                with gr.Column(scale=4, min_width=300, elem_id="library-panel", variant="panel"):
                    picker = gr.Dropdown(choices=choices(), label="Select Saved Case Record", info="Pick a case from the database to inspect details.")
                    with gr.Row():
                        refresh = gr.Button("🔄 Refresh List", size="sm")
                        load = gr.Button("👁️ Open Selected Case", variant="primary", size="sm")
                    manager_photo = gr.Image(type="pil", label="Submitted Evidence Photo", interactive=False, height=240)
                    reviewed = gr.Button("✅ Mark Case as Reviewed", variant="secondary")
                    gr.HTML('<p class="help-line">Auditing records records manager validation without replacing certified agronomic diagnosis.</p>')

                with gr.Column(scale=6, min_width=340, elem_id="case-panel", variant="panel"):
                    manager_brief = gr.HTML(empty_brief("Select a Case Record", "Choose a case from the dropdown on the left and click 'Open Selected Case' to inspect."))
                    with gr.Accordion("💬 Append Evidence / Re-analyze Case", open=False):
                        manager_answer = gr.Textbox(label="Additional Evidence / Follow-up Notes", max_length=2000)
                        manager_retry = gr.Button("🔄 Update Case Record", variant="secondary")
                    with gr.Accordion("🔍 Raw Inspection JSON & Audit Log", open=False):
                        record = gr.JSON()

        with gr.Tab("⚡ Architecture & Knowledge"):
            gr.Markdown(
                """
### 🏗️ Hapus Scout System Architecture

```
  ┌───────────────────────────┐
  │  Field Worker / Manager   │
  │  Mobile / Web Interface   │
  └─────────────┬─────────────┘
                │ HTTP Request (Photo + Notes)
                ▼
  ┌───────────────────────────┐
  │   Gradio Enterprise UI    │
  │   (Running in Colab)      │
  └─────────────┬─────────────┘
                │ Structured Prompt + Vision Tensor
                ▼
  ┌───────────────────────────┐
  │   Qwen3-VL Vision LLM     │
  │   (4-Bit GPU Inference)   │
  └─────────────┬─────────────┘
                │ JSON Triage Output
                ▼
  ┌───────────────────────────┐
  │  Grounded Reference Pack  │
  │ (ICAR / NHB Mango Rules) │
  └───────────────────────────┘
```

---

### 🛡️ Enterprise Guardrails & Safety Design
1. **Separation of Evidence vs Explanation**: Visual symptoms are kept strictly distinct from unconfirmed hypotheses.
2. **Anti-Hallucination Constraints**: Model refuses to make predictions when photo quality is unclear or irrelevant.
3. **Agronomic Scope Limits**: Zero automated chemical prescriptions, dosage calculations, or yield guarantees.
4. **Auditability**: Every case maintains complete revision history and timing metrics.

---

### 📚 Grounded Reference Documents
"""
                + "\n".join(f'- **[{r["title"]}]({r["url"]})**: {r["scope"]}' for r in REFERENCES)
            )

        # Event Wireups
        preset1_btn.click(set_preset_1, outputs=[location, part, observation])
        preset2_btn.click(set_preset_2, outputs=[location, part, observation])
        preset3_btn.click(set_preset_3, outputs=[location, part, observation])

        send.click(submit, [photo, location, part, observation], [current, brief, answer, picker])
        update.click(follow, [current, answer], [brief, picker])
        refresh.click(lambda: gr.update(choices=choices()), outputs=picker)
        load.click(open_case, picker, [manager_id, manager_brief, manager_photo, record])
        reviewed.click(review, manager_id, [manager_brief, record, picker])
        manager_retry.click(follow, [manager_id, manager_answer], [manager_brief, picker]).then(
            lambda case_id: service.store.get(case_id), manager_id, record
        )

    return demo.queue(default_concurrency_limit=1, max_size=12)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--ui-only", action="store_true", help="Verify UI without loading a model; analysis will be unavailable.")
    args = parser.parse_args()
    model = VisionModel()
    if not args.ui_only:
        print("Loading Qwen from the configured model folder; first startup can take several minutes.", flush=True)
        model.load()
    service = ScoutService(CaseStore(os.environ.get("SCOUT_DATA_DIR", "data/cases")), model)
    auth = None
    if args.share:
        password = os.environ.get("SCOUT_PASSWORD") or secrets.token_urlsafe(12)
        print(f"Demo login: scout | Password: {password}", flush=True)
        auth = ("scout", password)
    build_app(service).launch(share=args.share, auth=auth, server_name="127.0.0.1", max_file_size="10mb", show_error=False)


if __name__ == "__main__":
    main()
