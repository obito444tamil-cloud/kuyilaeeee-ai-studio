# KUYILAEEEE!!

Streamlit app for image generation, image editing, and Gemini image Q&A/OCR.
Choose a visual style preset when generating, then send the latest generated
image directly into the editor for another iteration.

Image generation tries the six configured providers in order: Gemini,
Pollinations, Hugging Face, Cloudflare Workers AI, AI Horde, and NVIDIA NIM.
Provider free quotas and trials are limited and can change. The app does not
configure payment, but cannot inspect provider account billing settings. Keep
provider billing disabled and set any available API-key budgets to zero-cost
credits only.

## Run locally

1. Install Python 3.10 or newer.
2. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   streamlit run nano_banana_app.py
   ```

4. Add provider credentials in the sidebar. You can create them here:
   - [Gemini](https://aistudio.google.com/apikey)
   - [Pollinations](https://enter.pollinations.ai/keys) — configure the key's
     budget to free credits only.
   - [Hugging Face](https://huggingface.co/settings/tokens) — free accounts
     receive a small monthly inference credit.
   - [Cloudflare Workers AI](https://dash.cloudflare.com/) — use a Workers Free
     account and supply its API token and account ID.
   - [AI Horde](https://aihorde.net/register) — community-powered; queue times
     can vary.
   - [NVIDIA NIM](https://build.nvidia.com/) — free API trial limits apply.

   Keys entered in the app stay in the Streamlit session and are not written to
   files. Never commit keys or paste them into chat.

## Run the tests

```powershell
python -m unittest discover -s tests
```

## Deploy with Streamlit Community Cloud

Push this folder to a GitHub repository, create an app at
[share.streamlit.io](https://share.streamlit.io/), and select
`nano_banana_app.py` as the entry point. Add any needed provider credentials
under the app's Secrets settings using the environment names above
(`GEMINI_API_KEY`, `POLLINATIONS_API_KEY`, `HUGGINGFACE_API_KEY`,
`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `AI_HORDE_API_KEY`, and
`NVIDIA_API_KEY`). Do not commit API keys to the repository.
