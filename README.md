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

## Live web page

Open the deployed KUYILAEEEE!! studio at
<https://kuyilaeeee-ai-studio-s8e5uwfhuog7zyoa2orpfn.streamlit.app/>.
The web page is live; image generation, editing, and image analysis require
provider credentials configured in the hosted app's Secrets settings.

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

   For deployment, add keys in the Streamlit app's **Settings → Secrets**.
   Local credentials can be entered in the sidebar or placed in
   `.streamlit/secrets.toml` (keep that file out of version control). The app
   reads Streamlit Secrets first, then environment variables, and displays
   configured values only in password-masked fields.

   Example Secrets configuration:

   ```toml
   GEMINI_API_KEY = "your-gemini-key"
   POLLINATIONS_API_KEY = "your-pollinations-key"
   HUGGINGFACE_API_KEY = "your-huggingface-token"
   CLOUDFLARE_API_TOKEN = "your-cloudflare-token"
   CLOUDFLARE_ACCOUNT_ID = "your-cloudflare-account-id"
   AI_HORDE_API_KEY = "your-ai-horde-key"
   NVIDIA_API_KEY = "your-nvidia-key"
   ```

   Replace only the values for providers you use. Never commit real keys or
   paste them into chat.

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
`NVIDIA_API_KEY`). The app reads these directly from Streamlit Secrets. Do not
commit API keys to the repository.
