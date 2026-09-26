"""Run in Colab through notebooks/launch_colab.ipynb."""
import argparse
import html
import os
import secrets
import gradio as gr
from scout.inspection import REFERENCES
from scout.model import VisionModel
from scout.service import ScoutService
from scout.storage import CaseStore

CSS = """
.gradio-container {max-width:1180px!important; margin:auto;}
#hero {background:#153d2e; color:#fff; padding:32px; border-radius:20px; margin-bottom:18px;}
#hero h1 {color:#fff!important; font-size:38px; margin:0 0 8px;}
#hero p {color:#e0eadf!important; font-size:17px;}
#hero .eyebrow {color:#ffce73!important; font-size:12px; letter-spacing:2px;}
.brief {padding:20px; border:1px solid #dce3d8; border-radius:12px; background:#fff; color:#213c2e;}
.brief :is(h2,h3,p,li,small,b) {color:#213c2e!important;}
.brief a {color:#146b47!important;}
.brief h3 {color:#153d2e; margin-top:20px;}
.brief li {margin:7px 0;}
.notice {padding:12px; background:#fff2d4; color:#684913; border-radius:8px;}
"""


def render(case):
    esc = lambda value: html.escape(str(value))
    parts = [f'<div class="brief"><small>CASE {esc(case["id"][:8])} · {esc(case["status"].upper())}</small>',
             f'<h2>{esc(case["report"]["location"])}</h2>',
             f'<p><b>Worker reported:</b> {esc(case["report"]["observation"])}</p>']
    if case["analysis_status"] != "ready":
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

    with gr.Blocks(title="Hapus Scout", theme=gr.themes.Soft(primary_hue="green", secondary_hue="amber"), css=CSS) as demo:
        gr.HTML('<div id="hero"><p class="eyebrow">HAPUS & MORE · DAY 1 PROTOTYPE</p><h1>Hapus Scout</h1><p>A clearer orchard report. A better next inspection.</p></div>')
        gr.Markdown("**Photo → AI observations → follow-up → manager review**  \nUse your own or permitted photos and fictional tree IDs. This shared demo has one team workspace.")
        with gr.Tab("Report & inspect"):
            current = gr.State("")
            with gr.Row():
                with gr.Column(scale=4):
                    photo = gr.Image(type="pil", label="Leaf or fruit photo", sources=["upload", "webcam"], height=280)
                    location = gr.Textbox(label="Tree or orchard block", placeholder="Example: Devgad demo / Block A / Tree 12", max_length=160)
                    part = gr.Radio(["Leaf", "Fruit", "Other / uncertain"], value="Leaf", label="What are you inspecting?")
                    observation = gr.Textbox(label="What did you notice?", placeholder="Describe when it started and whether nearby trees look similar.", lines=3, max_length=2000)
                    send = gr.Button("Save report & analyze photo", variant="primary")
                with gr.Column(scale=6):
                    brief = gr.HTML('<div class="brief"><h2>Your inspection brief</h2><p>Add a photo and observation to begin. No AI analysis has run yet.</p></div>')
                    answer = gr.Textbox(label="Answer the AI's questions", lines=2, max_length=2000)
                    update = gr.Button("Update brief / retry analysis")
        with gr.Tab("Manager's cases"):
            gr.Markdown("Open a case to review its photo, latest brief, and full revision history. Reviewing records a human workflow status; it does not validate a diagnosis.")
            picker = gr.Dropdown(choices=choices(), label="Saved cases")
            refresh = gr.Button("Refresh cases")
            load = gr.Button("Open case", variant="primary")
            manager_id = gr.State("")
            with gr.Row():
                manager_photo = gr.Image(type="pil", label="Submitted photo", interactive=False)
                manager_brief = gr.HTML()
            manager_answer = gr.Textbox(label="Additional evidence / answers", max_length=2000)
            manager_retry = gr.Button("Update this case / retry AI")
            reviewed = gr.Button("Mark reviewed")
            with gr.Accordion("Full case record & revision history", open=False):
                record = gr.JSON()
        with gr.Tab("About & evidence"):
            gr.Markdown("### How Scout works\nQwen3-VL reads the photo with the worker's report and a small static reference pack. Follow-up answers trigger a new model call on the same photo. Cases persist in Drive when launched through our notebook.\n\n### Prototype limits\nNo agricultural fine-tuning or accuracy validation. English output; Marathi input is experimental. No prescriptions, automatic treatment, or fabricated fallback analysis. The app is available only while Colab and its share link are active.\n\n### Reference pack\n" + "\n".join(f'- [{r["title"]}]({r["url"]}): {r["scope"]}' for r in REFERENCES))
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
        print("Loading Qwen from Drive; the first startup can take several minutes.", flush=True)
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
