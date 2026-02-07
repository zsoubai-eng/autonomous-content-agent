# Environment Variables Setup - Phase 27: The Infinite Factory

## New Required Environment Variables

Add these to your `.env` file:

```env
# The Strategist (Cerebras API)
CEREBRAS_API_KEY=your_cerebras_api_key_here

# The Artist (Cloudflare Workers AI)
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id_here
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token_here
```

## How to Get API Keys

### Cerebras API Key
1. Visit https://www.cerebras.ai/
2. Sign up for an account
3. Navigate to API settings
4. Generate an API key
5. Copy the key to `CEREBRAS_API_KEY` in your `.env`

### Cloudflare API Credentials
1. Visit https://dash.cloudflare.com/
2. Sign in to your Cloudflare account
3. Go to Workers & Pages → Overview
4. Find your Account ID (in the right sidebar)
5. Go to My Profile → API Tokens
6. Create a new token with "Workers AI" permissions
7. Copy Account ID to `CLOUDFLARE_ACCOUNT_ID`
8. Copy API Token to `CLOUDFLARE_API_TOKEN`

## Existing Environment Variables

The following variables are still used (for fallback):
- `GEMINI_API_KEY` or `GEMINI_API_KEY_1` (Backup Brain)
- `GEMINI_API_KEY_2` (Backup Brain)
- `GROQ_API_KEY` (Tertiary Brain)
- `ELEVENLABS_API_KEY` (Optional - Premium TTS)

## Verification

After adding the keys, run:
```bash
python main.py
```

You should see:
- "🧠 The Strategist (Cerebras): Generating storyboard..."
- "🎨 The Artist (Flux): Generating image..."
- "🎬 The Animator: Creating video from image..."

If you see fallback messages, check your API keys.
