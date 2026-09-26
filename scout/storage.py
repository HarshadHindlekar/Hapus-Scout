"""Atomic JSON files suitable for a single Colab process and mounted Drive."""
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from PIL import Image, ImageOps


def now():
    return datetime.now(timezone.utc).isoformat()


class CaseStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()

    def folder(self, case_id):
        if not re.fullmatch(r"[0-9a-f]{32}", case_id or ""):
            raise ValueError("Invalid case ID.")
        return self.root / case_id

    def save(self, case):
        folder = self.folder(case["id"])
        temporary = folder / "case.tmp"
        with self.lock:
            temporary.write_text(json.dumps(case, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(temporary, folder / "case.json")

    def create(self, image, report):
        case_id = uuid.uuid4().hex
        folder = self.folder(case_id)
        folder.mkdir()
        # Store a bounded, metadata-free copy; never publish the Drive root.
        picture = ImageOps.exif_transpose(image).convert("RGB")
        picture.thumbnail((1600, 1600))
        picture.save(folder / "photo.jpg", quality=90)
        case = dict(id=case_id, created_at=now(), report=report, status="open",
                    analysis_status="pending", revisions=[], error=None)
        self.save(case)
        return case

    def get(self, case_id):
        return json.loads((self.folder(case_id) / "case.json").read_text(encoding="utf-8"))

    def photo(self, case_id):
        with Image.open(self.folder(case_id) / "photo.jpg") as image:
            return image.copy()

    def list(self):
        cases = []
        for path in self.root.glob("*/case.json"):
            cases.append(json.loads(path.read_text(encoding="utf-8")))
        return sorted(cases, key=lambda case: case["created_at"], reverse=True)

    def reviewed(self, case_id):
        with self.lock:
            case = self.get(case_id)
            case.update(status="reviewed", reviewed_at=now())
            self.save(case)
        return case
