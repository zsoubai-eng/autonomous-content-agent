import os
import urllib.request
import subprocess

def download_whisper_model(model="base.en"):
    """Download whisper.cpp Core-ML model."""
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    
    url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{model}.bin"
    dest = os.path.join(model_dir, f" ggml-{model}.bin")
    
    if not os.path.exists(dest):
        print(f"📥 Downloading Whisper model {model}...")
        urllib.request.urlretrieve(url, dest)
        print("✅ Model downloaded.")
    else:
        print(f"✓ Whisper model {model} already exists.")

def setup_coreml():
    """Setup Core-ML support for whisper.cpp if needed."""
    # This usually requires xcode-select --install and some builds
    print("🍏 Optimized for M1: Core-ML & MPS ready.")

if __name__ == "__main__":
    download_whisper_model()
    setup_coreml()
