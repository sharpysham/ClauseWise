"""
onnx_export.py — Export classifier to ONNX + apply INT8 quantization via PyTorch.

Run this ONCE before the demo.

Usage:
    python -m ai_engine.onnx_export

Output files:
    models/clausewise_classifier.onnx          (ONNX export for runtime inference)
    models/clausewise_quantized.pt             (INT8 quantized PyTorch model)
"""

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import onnx
import onnxruntime as ort

# ── Config ───────────────────────────────────────────────────────────────────
MODEL_NAME  = "cross-encoder/nli-MiniLM2-l6-h768"
OUTPUT_DIR  = Path("models")
ONNX_PATH   = OUTPUT_DIR / "clausewise_classifier.onnx"
QUANT_PATH  = OUTPUT_DIR / "clausewise_quantized.pt"


def export_to_onnx():
    """Export the HuggingFace model to ONNX."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("[1/3] Loading model and exporting to ONNX...")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    dummy_inputs = tokenizer(
        "The contractor shall pay all damages.",
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=128
    )

    with torch.no_grad():
        torch.onnx.export(
            model,
            args=(dummy_inputs["input_ids"], dummy_inputs["attention_mask"]),
            f=str(ONNX_PATH),
            input_names=["input_ids", "attention_mask"],
            output_names=["logits"],
            dynamic_axes={
                "input_ids":      {0: "batch_size"},
                "attention_mask": {0: "batch_size"},
                "logits":         {0: "batch_size"},
            },
            opset_version=18,
            do_constant_folding=True,
        )

    print(f"      ✓ ONNX model saved to: {ONNX_PATH}")
    return tokenizer, model


def quantize_pytorch(model):
    """
    Apply INT8 dynamic quantization using PyTorch directly.
    This avoids the onnxruntime shape inference bug entirely.
    Quantizes Linear layers (the bulk of transformer weight size).
    """
    print("[2/3] Applying INT8 quantization via PyTorch...")

    quantized = torch.quantization.quantize_dynamic(
        model,
        {torch.nn.Linear},   # quantize all Linear layers
        dtype=torch.qint8
    )

    torch.save(quantized.state_dict(), str(QUANT_PATH))
    print(f"      ✓ Quantized weights saved to: {QUANT_PATH}")


def verify_onnx_inference(tokenizer):
    """Run a test inference with ONNX Runtime to confirm export worked."""
    print("[3/3] Verifying ONNX Runtime inference...")

    session = ort.InferenceSession(
        str(ONNX_PATH),
        providers=["CPUExecutionProvider"]
    )

    inputs = tokenizer(
        "The contractor shall pay $10,000 in damages within 30 days.",
        return_tensors="np",
        padding="max_length",
        truncation=True,
        max_length=128
    )

    expected = {i.name for i in session.get_inputs()}
    ort_inputs = {k: v for k, v in inputs.items() if k in expected}
    outputs = session.run(None, ort_inputs)

    print(f"      ✓ Inference successful! Output shape: {outputs[0].shape}")
    print(f"\n✅ All done! Your models are ready:")
    print(f"   ONNX model:       {ONNX_PATH}")
    print(f"   Quantized weights: {QUANT_PATH}")
    print(f"\n   ClauseWise AI engine is fully set up! 🚀")


if __name__ == "__main__":
    tokenizer, model = export_to_onnx()
    quantize_pytorch(model)
    verify_onnx_inference(tokenizer)
