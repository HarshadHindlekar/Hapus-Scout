"""HTTP smoke check against `python app.py --ui-only`; uses a synthetic blank image.

Run separately from unit tests. Creates one explicitly labelled test case.
"""
import tempfile
from pathlib import Path
from PIL import Image
from gradio_client import Client, handle_file

client = Client("http://127.0.0.1:7860", verbose=False)
with tempfile.TemporaryDirectory() as folder:
    photo = Path(folder) / "synthetic-ui-test.png"
    Image.new("RGB", (64, 64), "green").save(photo)
    brief, _, dropdown = client.predict(handle_file(str(photo)), "UI TEST - synthetic",
                                       "Leaf", "Synthetic blank image; testing outage handling only.", api_name="/submit")
    assert "unavailable" in brief.lower()
    case_id = dropdown["choices"][0][1]
    opened, saved_photo, record = client.predict(case_id, api_name="/open_case")
    assert record["analysis_status"] == "unavailable"
    assert record["revisions"] == []
    assert saved_photo
    _, reviewed, _ = client.predict(api_name="/review")
    assert reviewed["status"] == "reviewed"
    retry, _ = client.predict("A synthetic follow-up", api_name="/follow_1")
    assert "unavailable" in retry.lower()
print("PASS: HTTP upload, saved unavailable case, photo retrieval, review, retry. No AI output simulated.")
