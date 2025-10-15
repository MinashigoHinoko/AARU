import torch
from diffusers import StableDiffusionXLImg2ImgPipeline
from PIL import Image
from pathlib import Path
def get_device():
    """
    Prüft automatisch, ob CUDA oder MPS verfügbar ist,
    sonst wird auf CPU gewechselt.
    Gibt das gewählte Gerät und den Grund aus.
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("✅ Using GPU (CUDA)")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ Using Apple MPS backend")
    else:
        device = torch.device("cpu")
        print("🧠 Using CPU (no GPU acceleration available)")
    return device

device = get_device()

# Testausgabe
print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# --- Ordner-Pfade ---
model_id = "stabilityai/stable-diffusion-xl-base-1.0"
prompt_dir = Path("generated_prompts")
base_dir = Path("base_image")
out_dir = Path("outputs")
out_dir.mkdir(exist_ok=True)

# --- Modell laden ---
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    use_safetensors=True
).to(device)

# --- Prompts abarbeiten ---
for prompt_file in prompt_dir.glob("*.txt"):
    base_name = prompt_file.stem.replace("prompt_", "")
    base_image_path = base_dir / f"{base_name}.png"
    if not base_image_path.exists():
        print(f"❌ Kein Basisbild gefunden für {base_name}")
        continue

    prompt = prompt_file.read_text(encoding="utf-8")
    image = Image.open(base_image_path).convert("RGB")

    print(f"🔹 Generiere Overlay für {base_name}...")

    result = pipe(
        prompt=prompt,
        image=image,
        strength=0.20,      # gering = original bleibt fast unverändert
        guidance_scale=7.5  # höher = strenger am Prompt
    ).images[0]

    result.save(out_dir / f"{base_name}_overlay.png")
    print(f"✅ Fertig: {base_name}_overlay.png")
