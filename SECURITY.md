# 🛡️ Security & Privacy Guide

This project is built to be **100% local-first**. Your privacy and data security are our top priorities.

## 🗝️ Handling Secrets
All API keys and tokens are stored in:
- `.env` (OpenAI, Gemini, etc.)
- `client_secrets.json` (Google App credentials)
- `token.json` (Your personal YouTube/Calendar access)

**NEVER share these files or commit them to GitHub.** They are already listed in `.gitignore` by default.

## 🆘 If You Accidentally Pushed a Secret
If you realize you have committed and pushed a secret (like an OpenAI key) to a public repository, follow these steps immediately:

1. **Revoke the Key**:
   - For OpenAI: Go to [platform.openai.com](https://platform.openai.com/api-keys) and delete the exposed key.
   - For Google: Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and delete the client secret or revoke the OAuth token.
2. **Remove from Git History**:
   - Use a tool like [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) or `git filter-repo` to scrub the secret from your entire history.
3. **Generate New Keys**:
   - Create fresh keys and update your `.env` file locally.

## 🔒 Automated Protection
The `secure.py` script runs before and after execution to:
- Verify `.gitignore` is correctly configured.
- Scan for accidental secret leaks in staged files.
- Refuse to run if keys are detected in tracked files.

## 🚫 Pipeline Force-Abort
The Kedro pipeline will **strictly abort** if `OPENAI_API_KEY` or `token.json` is missing. No data will be processed until the environment is secure.
