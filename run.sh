#!/bin/bash

# Zero-Cost Content Factory - Legacy Wrapper
# Reuses main.py logic for automation

AUTO_APPROVE=0

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --auto-approve) AUTO_APPROVE=1 ;;
        *) ARGS+=("$1") ;;
    esac
    shift
done

# Check if OpenAI key is present
if [ -z "$OPENAI_API_KEY" ]; then
    # Try to load from .env
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY is missing. Please set it in your .env file."
    exit 1
fi

# Run the main production cycle
# If a URL is passed, we might need to handle it differently, 
# but for now, we'll map to run_production_cycle or similar
python3 main.py "${ARGS[@]}"
