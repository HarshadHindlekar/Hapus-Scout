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
body,.dark {background:#f5f5ef!important; color:#243d32!important;}
.gradio-container {width:100%!important; max-width:1240px!important; box-sizing:border-box; margin:auto; padding:clamp(14px,2vw,28px)!important; font-family:Arial,sans-serif!important;}
.gradio-container .app {padding:0!important;}
.gradio-container .html-container {padding:0!important;}
#hero {display:flex; align-items:center; justify-content:space-between; gap:24px; padding:8px 0 24px; border-bottom:1px solid #dce2d8;}
#hero h1 {color:#173f30!important; font-size:30px; letter-spacing:-1px; margin:0; line-height:1.2;}
#hero p {color:#65746b!important; font-size:14px; margin:7px 0 0;}
#hero .eyebrow {color:#607568!important; font-size:10px; font-weight:700; letter-spacing:2px; margin:0 0 8px;}
.brand {display:flex; align-items:center; gap:14px;}
.brandmark {display:grid;place-items:center;width:48px;height:48px;background:#1b503d;color:#f8d777;border-radius:15px;font:700 28px Georgia,serif;}
.workspace-tag {font-size:12px; color:#536a5b; border:1px solid #d4dfd4; padding:8px 12px; border-radius:24px; white-space:nowrap;}
.intro {padding:8px 0 0;}
.intro h2 {font-size:25px!important; letter-spacing:-.6px; color:#203c2d!important; margin:0 0 8px!important;}
.intro p {font-size:14px!important;color:#65746b!important;margin:0!important;}
.steps {display:flex;gap:24px;padding:12px 0 16px;color:#67776c;font-size:12px;}
.steps b {display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#e6ecdf;color:#35533e;margin-right:7px;font-size:10px;}
#storage-note {background:#fff5dd;border:1px solid #eddfb9;padding:10px 14px!important;border-radius:9px;color:#765a21;font-size:12px;}
.tab-nav {border-bottom:1px solid #dce2d8!important;gap:18px!important;margin-bottom:18px!important;}
.tab-nav button {padding:12px 2px!important;font-size:14px!important;color:#65746b!important;border-radius:0!important;}
.tab-nav button.selected {color:#1b503d!important;border-bottom:3px solid #1b503d!important;font-weight:700!important;}
#report-panel,#brief-panel,#library-panel,#case-panel {background:#fff!important;border:1px solid #e0e5dc!important;border-radius:16px!important;padding:22px!important;box-shadow:0 3px 14px #223f2805;}
.section-head {margin-bottom:6px;}
.section-head h3 {font-size:18px!important;color:#203c2d!important;margin:0 0 5px!important;}
.section-head p {font-size:12px!important;color:#718075!important;margin:0!important;}
#photo-input {border:1px dashed #c2d1c1!important;background:#f8faf5!important;border-radius:12px!important;}
.brief {padding:24px;border:1px solid #dce3d8;border-radius:14px;background:#fff;color:#213c2e;line-height:1.6;}
.brief h2 {font-size:23px!important;letter-spacing:-.4px;}
.brief small {font-size:11px;letter-spacing:.5px;}
.brief :is(h2,h3,p,li,small,b) {color:#213c2e!important;}
.brief a {color:#146b47!important;}
.brief h3 {font-size:14px!important;border-top:1px solid #e9ede6;padding-top:16px;margin-top:20px;}
.brief li {margin:7px 0;font-size:14px;}
.notice {padding:12px;background:#fff5df;color:#684913;border-radius:8px;font-size:12px;}
.empty-brief {min-height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:30px;border:1px dashed #ccd8c9;border-radius:14px;background:#f9fbf6;}
.empty-icon {font:30px Georgia,serif;color:#54745b;background:#e7efdf;border-radius:50%;width:62px;height:62px;display:grid;place-items:center;margin-bottom:16px;}
.empty-brief h3 {color:#24442f!important;font-size:19px!important;margin:0 0 10px!important;}
.empty-brief p {color:#718075!important;max-width:330px;line-height:1.7;font-size:13px!important;margin:0!important;}
.help-line {font-size:11px!important;color:#7a857b!important;line-height:1.5;}
.gradio-container button {cursor:pointer;}
.gradio-container button:focus-visible {outline:3px solid #bf9b49!important;outline-offset:3px;}
footer {opacity:.65;}
@media(max-width:640px) {.gradio-container{padding:14px!important;}#hero{gap:10px;padding-bottom:18px;}#hero h1{font-size:25px;}.workspace-tag{display:none;}.intro h2{font-size:22px!important;}.steps{gap:10px;font-size:10px;}#report-panel,#brief-panel,#library-panel,#case-panel{padding:16px!important;}.empty-brief{min-height:230px;padding:20px;}.tab-nav{gap:12px!important;}.tab-nav button{font-size:12px!important;}}
"""


def scout_theme():
    theme = gr.themes.Base(primary_hue="green", neutral_hue="stone", font=["Arial", "sans-serif"])
    values = dict(body_background_fill="#f5f5ef", body_text_color="#243d32", body_text_color_subdued="#718075",
                  background_fill_primary="#ffffff", background_fill_secondary="#f4f7ef", border_color_primary="#dce3d8",
                  block_background_fill="#ffffff", block_border_width="0px", block_label_background_fill="transparent",
                  block_label_text_color="#435a49", block_title_text_color="#435a49", block_title_background_fill="transparent",
                  block_label_text_size="12px", block_label_text_weight="600", block_label_padding="4px 0",
                  block_shadow="none", input_background_fill="#fafbf8", input_border_color="#dce3d8",
                  input_border_color_focus="#457758", input_shadow="none", input_text_size="14px", input_radius="8px",
                  input_placeholder_color="#899488", button_primary_background_fill="#1b503d",
                  button_primary_background_fill_hover="#123d2d", button_primary_text_color="#ffffff",
                  button_primary_border_color="#1b503d", button_secondary_background_fill="#f0f4eb",
                  button_secondary_background_fill_hover="#e4ecdc", button_secondary_text_color="#35533e",
                  button_secondary_border_color="#d7e1d2", button_large_radius="9px", button_large_text_size="14px",
                  checkbox_label_background_fill="#ffffff", checkbox_label_text_color="#536a5b",
                  checkbox_label_background_fill_selected="#edf4e7", checkbox_label_text_color_selected="#234d35",
                  checkbox_label_border_color="#dce3d8", checkbox_label_border_color_selected="#769274",
                  color_accent_soft="#e7efdf", panel_background_fill="#ffffff", block_padding="10px",
                  layout_gap="18px", block_radius="10px")
    parameters = inspect.signature(theme.set).parameters
    for name, value in list(values.items()):
        if name + "_dark" in parameters:
            values[name + "_dark"] = value
    return theme.set(**values)


def empty_brief(title, description):
    return f'<div class="empty-brief"><div class="empty-icon">⌕</div><h3>{title}</h3><p>{description}</p></div>'


def render(case):
    esc = lambda value: html.escape(str(value))
    parts = [f'<div class="brief"><small>CASE {esc(case["id"][:8])} · {esc(case["status"].upper())}</small>',
             f'<h2>{esc(case["report"]["location"])}</h2>',
             f'<p><b>Worker reported:</b> {esc(case["report"]["observation"])}</p>']
    if case["analysis_status"] == "pending":
        parts.append('<p class="notice">Report saved. Scout is examining your photo. Keep this page open.</p>')
    elif case["analysis_status"] != "ready":
        parts.append('<p class="notice">AI analysis unavailable or pending. Your photo and report are saved. Retry when the model is ready.</p>')
    if case["revisions"]:
        revision = case["revisions"][-1]
        result = revision["analysis"]
        if case["analysis_status"] != "ready":
            parts.append('<b>Previous successful brief — latest attempt did not update this.</b>')
        parts.extend([f'<p>{esc(result["summary"])}</p>', f'<p>Image evidence: <b>{esc(result["image_quality"])}</b></p>'])
        for key, title in [("observations", "Visible observations"), ("possible_explanations", "Possible explanations · unconfirmed"),
                           ("questions", "Questions for the worker"), ("next_checks", "Next evidence to collect"), ("limitations", "What remains uncertain")]:
            items = result[key]
            parts.append(f'<h3>{title}</h3><ul>' + "".join(f'<li>{esc(item)}</li>' for item in items) + '</ul>' if items else f'<h3>{title}</h3><p>None supplied.</p>')
        sources = [r for r in REFERENCES if r["id"] in result["reference_ids"]]
        if sources:
            parts.append('<h3>Reference context used</h3>' + "".join(f'<p><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["title"])}</a></p>' for r in sources))
        parts.append(f'<p><small>{esc(revision["model"])} · {esc(revision["seconds"])}s · revision {len(case["revisions"])}</small></p>')
    parts.append('<p class="notice">Inspection support only. AI output may be wrong; a farm manager or agronomist must verify it. No confirmed diagnosis or treatment prescription.</p></div>')
    return "".join(parts)


def build_app(service):
    def choices():
        return [(f'{c["report"]["location"]} · {c["status"]} · {c["id"][:8]}', c["id"]) for c in service.store.list()]

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

    with gr.Blocks(title="Hapus Scout", theme=scout_theme(), css=CSS) as demo:
        gr.HTML('<header id="hero"><div class="brand"><div class="brandmark">h.</div><div><p class="eyebrow">HAPUS & MORE</p><h1>Hapus Scout</h1></div></div><span class="workspace-tag">Orchard inspection workspace</span></header>')
        gr.HTML('<div class="intro"><h2>A closer look. A clearer next step.</h2><p>Turn a leaf or fruit observation into a useful inspection report.</p></div><div class="steps"><span><b>01</b> Capture evidence</span><span><b>02</b> Explore observations</span><span><b>03</b> Review the case</span></div>')
        if os.environ.get("SCOUT_STORAGE_MODE") == "temporary":
            gr.HTML('<div id="storage-note"><b>Session-only workspace</b> · Your reports are saved for this session and will be lost when the Colab runtime is deleted.</div>')
        with gr.Tab("New inspection"):
            current = gr.State("")
            with gr.Row():
                with gr.Column(scale=4, min_width=300, elem_id="report-panel", variant="panel"):
                    gr.HTML('<div class="section-head"><h3>What did you find?</h3><p>Add a clear photo and a little field context.</p></div>')
                    photo = gr.Image(type="pil", label="Leaf or fruit photo", sources=["upload", "webcam"], height=220, elem_id="photo-input")
                    location = gr.Textbox(label="Tree or orchard block", placeholder="e.g. Block A / Tree 12", max_length=160)
                    part = gr.Radio(["Leaf", "Fruit", "Other / uncertain"], value="Leaf", label="What are you inspecting?")
                    observation = gr.Textbox(label="What did you notice?", placeholder="When did it start? Are nearby trees affected?", lines=3, max_length=2000)
                    send = gr.Button("Analyze inspection →", variant="primary")
                    gr.HTML('<p class="help-line">Use permitted photos and fictional tree IDs for this demo.</p>')
                with gr.Column(scale=6, min_width=300, elem_id="brief-panel", variant="panel"):
                    gr.HTML('<div class="section-head"><h3>Inspection brief</h3><p>Visible evidence, open questions and what to check next.</p></div>')
                    brief = gr.HTML(empty_brief("Your next step starts here", "Add a photo and field note, then select Analyze inspection. Your AI brief will appear here."))
                    with gr.Accordion("Add evidence or retry analysis", open=False):
                        answer = gr.Textbox(label="Answers or additional observations", placeholder="After analysis, answer Scout's questions here.", lines=2, max_length=2000)
                        update = gr.Button("Update inspection brief", variant="secondary")
                    gr.HTML('<p class="help-line">AI supports inspection. A farm manager or agronomist should verify the findings.</p>')
        with gr.Tab("Case library"):
            gr.HTML('<div class="section-head"><h3>Your orchard cases</h3><p>Review submitted evidence and keep track of what needs a closer look.</p></div>')
            manager_id = gr.State("")
            with gr.Row():
                with gr.Column(scale=3, min_width=280, elem_id="library-panel", variant="panel"):
                    picker = gr.Dropdown(choices=choices(), label="Select a case", info="No cases yet? Create your first inspection in the other tab.")
                    with gr.Row():
                        refresh = gr.Button("Refresh", size="sm")
                        load = gr.Button("Open case", variant="primary", size="sm")
                    manager_photo = gr.Image(type="pil", label="Submitted photo", interactive=False, height=230)
                    reviewed = gr.Button("Mark as reviewed", variant="secondary")
                    gr.HTML('<p class="help-line">Reviewed records a human check, not a confirmed diagnosis. This demo uses one shared team workspace.</p>')
                with gr.Column(scale=6, min_width=300, elem_id="case-panel", variant="panel"):
                    manager_brief = gr.HTML(empty_brief("Every observation has a story", "Choose a saved case to see the photo evidence, inspection brief and review history."))
                    with gr.Accordion("Add evidence or retry analysis", open=False):
                        manager_answer = gr.Textbox(label="Additional evidence / answers", max_length=2000)
                        manager_retry = gr.Button("Update this case", variant="secondary")
                    with gr.Accordion("Case record & revision history", open=False):
                        record = gr.JSON()
        with gr.Tab("How it works"):
            gr.Markdown("### How Scout works\nQwen3-VL reads the photo with the worker's report and a small static reference pack. Follow-up answers trigger a new model call on the same photo. Drive mode preserves cases in Drive; session-only mode stores them temporarily in Colab.\n\n### Prototype limits\nNo agricultural fine-tuning or accuracy validation. English output; Marathi input is experimental. No prescriptions, automatic treatment, or fabricated fallback analysis. The app is available only while Colab and its share link are active.\n\n### Reference pack\n" + "\n".join(f'- [{r["title"]}]({r["url"]}): {r["scope"]}' for r in REFERENCES))
        send.click(submit, [photo, location, part, observation], [current, brief, answer, picker])
        update.click(follow, [current, answer], [brief, picker])
        refresh.click(lambda: gr.update(choices=choices()), outputs=picker)
        load.click(open_case, picker, [manager_id, manager_brief, manager_photo, record])
        reviewed.click(review, manager_id, [manager_brief, record, picker])
        manager_retry.click(follow, [manager_id, manager_answer], [manager_brief, picker]).then(
            lambda case_id: service.store.get(case_id), manager_id, record)
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
