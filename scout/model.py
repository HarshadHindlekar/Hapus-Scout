"""Lazy GPU inference; no weights or model imports needed for storage/UI tests."""
import json
import os
from pathlib import Path
from threading import Lock

MODEL_ID = "Qwen/Qwen3-VL-4B-Instruct"


def validate_model(path):
    path = Path(path)
    config = json.loads((path / "config.json").read_text(encoding="utf-8"))
    if config.get("model_type") != "qwen3_vl":
        raise ValueError("Select a Transformers Qwen3-VL model folder, not GGUF or another model.")
    index = path / "model.safetensors.index.json"
    weights = ([path / name for name in set(json.loads(index.read_text())["weight_map"].values())]
               if index.exists() else [path / "model.safetensors"])
    if not weights or any(not p.is_file() or p.stat().st_size == 0 for p in weights):
        raise ValueError("The model folder has missing or empty weight shards.")
    return path


def discover_model(root):
    candidates = []
    for config in Path(root).rglob("config.json"):
        try:
            candidates.append(validate_model(config.parent))
        except (ValueError, KeyError, OSError):
            continue
    if len(candidates) != 1:
        raise ValueError(f"Found {len(candidates)} complete Qwen3-VL folders. Set MODEL_PATH in the launcher to the exact folder.")
    return candidates[0]


class VisionModel:
    def __init__(self):
        self.model = self.processor = None
        self.lock = Lock()

    def load(self):
        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig, Qwen3VLForConditionalGeneration
        if not torch.cuda.is_available():
            raise RuntimeError("GPU unavailable. In Colab choose Runtime > Change runtime type > T4 GPU.")
        path = validate_model(os.environ["SCOUT_MODEL_PATH"])
        # Processor assets are small; recover incomplete Drive processor bundles from the official model.
        try:
            processor = AutoProcessor.from_pretrained(str(path), local_files_only=True)
        except (OSError, ValueError, TypeError):
            processor = AutoProcessor.from_pretrained(MODEL_ID)
        config = json.loads((path / "config.json").read_text())
        kwargs = dict(device_map="auto", torch_dtype=torch.float16, attn_implementation="sdpa", local_files_only=True)
        if not config.get("quantization_config"):
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        model = Qwen3VLForConditionalGeneration.from_pretrained(str(path), **kwargs).eval()
        self.processor, self.model = processor, model

    def generate(self, image, prompt):
        import torch
        from qwen_vl_utils import process_vision_info
        with self.lock:
            if self.model is None:
                self.load()
            messages = [{"role": "user", "content": [
                {"type": "image", "image": image, "max_pixels": 512 * 512},
                {"type": "text", "text": prompt}]}]
            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            images, videos = process_vision_info(messages)
            inputs = self.processor(text=[text], images=images, videos=videos, padding=True, return_tensors="pt").to(self.model.device)
            with torch.inference_mode():
                output = self.model.generate(**inputs, max_new_tokens=1200, do_sample=False)
            return self.processor.batch_decode(output[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0]
