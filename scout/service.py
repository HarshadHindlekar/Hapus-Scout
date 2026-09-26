from time import monotonic
from scout.inspection import build_prompt, parse_analysis
from scout.model import MODEL_ID
from scout.storage import now


class ScoutService:
    def __init__(self, store, model):
        self.store, self.model = store, model

    def submit(self, image, location, part, observation):
        if image is None:
            raise ValueError("Upload a photo first.")
        if not location.strip() or not observation.strip():
            raise ValueError("Enter a tree/block reference and your observation.")
        if len(location) > 160 or len(observation) > 2000:
            raise ValueError("Use a short location and an observation under 2,000 characters.")
        return self.store.create(image, dict(location=location.strip(), part=part, observation=observation.strip()))

    def analyze(self, case_id, answers=""):
        if len(answers) > 2000:
            raise ValueError("Keep follow-up answers under 2,000 characters.")
        # Same process lock prevents a review or concurrent follow-up overwriting revisions.
        with self.store.lock:
            case = self.store.get(case_id)
            revisions = case["revisions"]
            previous = revisions[-1]["analysis"] if revisions else None
            started = monotonic()
            try:
                raw = self.model.generate(self.store.photo(case_id), build_prompt(case["report"], answers, previous))
                result = parse_analysis(raw)
                revisions.append(dict(at=now(), answers=answers, analysis=result, model=MODEL_ID,
                                      seconds=round(monotonic() - started, 2)))
                case.update(analysis_status="ready", status="open", error=None)
            except Exception as exc:
                # Preserve evidence and earlier successful revisions. Never substitute a canned diagnosis.
                case.update(analysis_status="unavailable", error=type(exc).__name__)
            self.store.save(case)
        return case
