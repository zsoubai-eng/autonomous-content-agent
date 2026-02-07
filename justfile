# AI Shorts Factory - M1 Orchestration

install-m1:
    @echo "🍏 Installing M1-optimized dependencies..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    # For MPS support on M1:
    pip install TTS faster-whisper kedro python-dotenv google-auth-oauthlib google-api-python-client
    python3 scripts/m1_setup.py

auth-google:
    @echo "🔑 Starting Google OAuth flow..."
    python3 scripts/auth_google.py

run:
    @echo "🚀 Running Kedro Shorts Pipeline..."
    ./secure.py
    kedro run --pipeline shorts

test:
    @echo "🧪 Running unit tests..."
    pytest tests/test_nodes.py

clean:
    @echo "🧹 Cleaning temporary artifacts..."
    rm -rf kedro_cli/data/02_intermediate/*
    rm -rf kedro_cli/data/07_model_output/*
    ./master_factory.py --cleanup-only

secure-check:
    @echo "🛡️ Running security check..."
    python3 secure.py --check

# ============================================
# AUTONOMOUS VIRAL FACTORY (Zero-Touch Mode)
# ============================================

auto-generate:
    @echo "🤖 Generating weekly batch (scrape + generate + schedule)..."
    python3 autonomous_scheduler.py --generate --num-videos 7

auto-publish:
    @echo "🚀 Executing scheduled publish..."
    python3 autonomous_scheduler.py --publish

auto-full:
    @echo "🤖 Full autonomous workflow..."
    python3 autonomous_scheduler.py --generate --num-videos 7
    @echo "✅ Review autonomous_schedule.json, then run: just auto-publish"
