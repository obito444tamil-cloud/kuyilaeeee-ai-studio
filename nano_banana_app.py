"""
KUYILAEEEE!! AI Studio
  1. Text → Image generation
  2. AI Image Editing (change text in image, restyle, remove objects...)
  3. Image → Text (extract info / OCR / Q&A from images)

Run:  streamlit run nano_banana_app.py
"""

import base64
from io import BytesIO
import os
import time
from urllib.parse import quote

import requests
import streamlit as st
from google import genai
from google.genai import errors
from PIL import Image, UnidentifiedImageError
from streamlit.errors import StreamlitSecretNotFoundError

st.set_page_config(page_title="KUYILAEEEE!!", page_icon="✨", layout="wide")
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 88% 3%, rgba(107, 76, 180, .22), transparent 36%),
            radial-gradient(ellipse at 5% 35%, rgba(255, 181, 48, .07), transparent 32%),
            #0b0d16;
        color: #f2f0f8;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #171528 0%, #11131e 100%);
        border-right: 1px solid rgba(255, 255, 255, .08);
    }
    .hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        padding: 1.5rem 1.8rem;
        margin: .25rem 0 1.5rem;
        border: 1px solid rgba(255, 255, 255, .1);
        border-radius: 22px;
        background:
            radial-gradient(circle at 88% 50%, rgba(255, 213, 74, .14), transparent 18rem),
            linear-gradient(115deg, rgba(255, 213, 74, .1), rgba(112, 76, 189, .23));
        box-shadow: 0 24px 70px rgba(0, 0, 0, .18);
    }
    .hero-copy {
        min-width: 0;
    }
    .hero-mark {
        flex: 0 0 auto;
        display: grid;
        width: 6rem;
        height: 6rem;
        place-items: center;
        border: 1px solid rgba(255, 255, 255, .16);
        border-radius: 1.8rem;
        background: rgba(255, 255, 255, .07);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .1);
        font-size: 3.3rem;
        transform: rotate(6deg);
    }
    .hero-kicker {
        color: #ffd54a;
        font-size: .76rem;
        font-weight: 750;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .hero h1 {
        margin: .3rem 0 .35rem;
        color: #fff;
        font-size: clamp(2rem, 4vw, 3.1rem);
        font-weight: 800;
        letter-spacing: -.045em;
    }
    .hero p {
        margin: 0;
        color: #c0bdcc;
        font-size: 1rem;
    }
    .workflow-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .85rem;
        margin: 0 0 1.35rem;
    }
    .workflow-card {
        display: flex;
        align-items: flex-start;
        gap: .8rem;
        min-height: 5rem;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(255, 255, 255, .09);
        border-radius: 16px;
        background: linear-gradient(140deg, rgba(255, 255, 255, .055), rgba(255, 255, 255, .025));
    }
    .workflow-number {
        display: grid;
        flex: 0 0 auto;
        width: 2rem;
        height: 2rem;
        place-items: center;
        border-radius: 10px;
        background: rgba(255, 213, 74, .12);
        color: #ffd54a;
        font-size: .76rem;
        font-weight: 800;
    }
    .workflow-card strong {
        display: block;
        color: #f4f0ff;
        font-size: .92rem;
    }
    .workflow-card p {
        margin: .2rem 0 0;
        color: #aaa7b9;
        font-size: .78rem;
        line-height: 1.4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: .55rem;
        border-bottom: 1px solid rgba(255, 255, 255, .1);
        padding-bottom: .2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3.25rem;
        padding: 0 1rem;
        border-radius: 12px 12px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255, 213, 74, .1);
    }
    .stButton > button[kind="primary"] {
        min-height: 3rem;
        border: 0;
        border-radius: 12px;
        background: linear-gradient(100deg, #ffd54a, #ffb72b);
        color: #211907;
        font-weight: 750;
    }
    .stButton > button[kind="primary"]:hover {
        border: 0;
        background: linear-gradient(100deg, #ffe276, #ffc554);
        color: #211907;
        box-shadow: 0 8px 28px rgba(255, 190, 44, .18);
    }
    [data-testid="stTextArea"] textarea,
    [data-testid="stTextInput"] input {
        border-radius: 12px;
    }
    [data-testid="stFileUploader"] section {
        border-radius: 14px;
    }
    [data-testid="stImage"] img {
        border: 1px solid rgba(255, 255, 255, .1);
        border-radius: 16px;
    }
    @media (max-width: 700px) {
        .block-container {
            padding-top: 1rem;
        }
        .hero {
            padding: 1.2rem;
        }
        .hero-mark {
            width: 4rem;
            height: 4rem;
            border-radius: 1.2rem;
            font-size: 2.2rem;
        }
        .workflow-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    <div class="hero">
      <div class="hero-copy">
        <div class="hero-kicker">YOUR CREATIVE AI WORKSPACE</div>
        <h1>✨ KUYILAEEEE!!</h1>
        <p>Dream it, refine it, and uncover what is inside your images.</p>
      </div>
      <div class="hero-mark" aria-hidden="true">🍌</div>
    </div>
    <div class="workflow-grid">
      <div class="workflow-card">
        <span class="workflow-number">01</span>
        <div><strong>Create</strong><p>Turn a clear idea into an original image.</p></div>
      </div>
      <div class="workflow-card">
        <span class="workflow-number">02</span>
        <div><strong>Refine</strong><p>Upload or keep iterating on your latest image.</p></div>
      </div>
      <div class="workflow-card">
        <span class="workflow-number">03</span>
        <div><strong>Understand</strong><p>Extract text, summaries, and visual answers.</p></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

IMAGE_MODELS = [
    "gemini-3.1-flash-lite-image",
    "gemini-3.1-flash-image",
    "gemini-3-pro-image",
    "gemini-2.5-flash-image",
]
TEXT_MODELS = ["gemini-2.5-flash", "gemini-3.1-flash-lite"]


def get_configured_value(secret_name, *environment_names):
    try:
        value = st.secrets.get(secret_name)
    except StreamlitSecretNotFoundError:
        value = None
    if value is not None and str(value).strip():
        return str(value).strip()
    for name in environment_names or (secret_name,):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def get_client():
    api_key = st.session_state.get("api_key", "").strip()
    return genai.Client(api_key=api_key) if api_key else None


def get_image_provider_keys():
    return {
        "gemini_key": st.session_state.get("api_key", "").strip(),
        "pollinations_key": st.session_state.get("pollinations_api_key", "").strip(),
        "huggingface_key": st.session_state.get("huggingface_api_key", "").strip(),
        "cloudflare_token": st.session_state.get("cloudflare_api_token", "").strip(),
        "cloudflare_account_id": st.session_state.get("cloudflare_account_id", "").strip(),
        "ai_horde_key": st.session_state.get("ai_horde_api_key", "").strip(),
        "nvidia_key": st.session_state.get("nvidia_api_key", "").strip(),
    }


def has_image_provider(keys):
    return any(
        (
            keys["gemini_key"],
            keys["pollinations_key"],
            keys["huggingface_key"],
            keys["cloudflare_token"] and keys["cloudflare_account_id"],
            keys["ai_horde_key"],
            keys["nvidia_key"],
        )
    )


def pil_to_bytes(img, fmt="PNG"):
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def load_image(uploaded_file):
    try:
        with Image.open(uploaded_file) as image:
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("The uploaded file is not a readable image.") from exc


def image_from_bytes(image_bytes):
    try:
        with Image.open(BytesIO(image_bytes)) as generated:
            return generated.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError("The image provider returned data that is not a readable image.") from exc


def generate_with_gemini(client, model, prompt, image=None, aspect_ratio=None):
    contents = [{"type": "text", "text": prompt}]
    if image is not None:
        contents.append(
            {
                "type": "image",
                "mime_type": "image/png",
                "data": base64.b64encode(pil_to_bytes(image)).decode("ascii"),
            }
        )
    request = {"model": model, "input": contents}
    if aspect_ratio and aspect_ratio != "Auto":
        request["response_format"] = {"type": "image", "aspect_ratio": aspect_ratio}
    response = client.interactions.create(**request)
    if not response.output_image or not response.output_image.data:
        raise RuntimeError("Gemini returned no image. Try another image model or provider.")
    return image_from_bytes(base64.b64decode(response.output_image.data))


def image_from_api_response(response):
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if (
        content_type.startswith("image/")
        or content_type == "application/octet-stream"
        or response.content.startswith((b"\x89PNG", b"\xff\xd8", b"RIFF"))
    ):
        return image_from_bytes(response.content)

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("The image provider returned an unexpected response.") from exc
    data = (payload.get("data") or [{}])[0]
    if data.get("b64_json"):
        return image_from_bytes(base64.b64decode(data["b64_json"]))
    if data.get("url"):
        image_response = requests.get(data["url"], timeout=90)
        image_response.raise_for_status()
        return image_from_bytes(image_response.content)
    raise RuntimeError("The image provider response contained no image.")


def generate_with_pollinations(api_key, model, prompt, image=None, aspect_ratio=None):
    headers = {"Authorization": f"Bearer {api_key}"}
    if image is None:
        params = {"model": model}
        if aspect_ratio and aspect_ratio != "Auto":
            params["aspectRatio"] = aspect_ratio
        response = requests.get(
            f"https://gen.pollinations.ai/image/{quote(prompt, safe='')}",
            headers=headers,
            params=params,
            timeout=120,
        )
    else:
        data = {
            "prompt": prompt,
            "model": model,
            "response_format": "b64_json",
            "image": "data:image/png;base64," + base64.b64encode(pil_to_bytes(image)).decode("ascii"),
        }
        response = requests.post(
            "https://gen.pollinations.ai/v1/images/edits",
            headers=headers,
            json=data,
            timeout=120,
        )
    return image_from_api_response(response)


def generate_with_huggingface(api_key, prompt, aspect_ratio=None):
    width, height = {
        "1:1": (1024, 1024),
        "3:2": (1024, 682),
        "4:3": (1024, 768),
        "9:16": (576, 1024),
        "16:9": (1024, 576),
    }.get(aspect_ratio, (1024, 1024))
    response = requests.post(
        "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-3-medium-diffusers",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"inputs": prompt, "parameters": {"width": width, "height": height}},
        timeout=180,
    )
    return image_from_api_response(response)


def generate_with_cloudflare(token, account_id, prompt, image=None, aspect_ratio=None):
    width, height = {
        "1:1": (1024, 1024),
        "3:2": (1024, 682),
        "4:3": (1024, 768),
        "9:16": (576, 1024),
        "16:9": (1024, 576),
    }.get(aspect_ratio, (1024, 1024))
    inputs = {"prompt": prompt, "width": width, "height": height}
    if image is not None:
        inputs["image_b64"] = base64.b64encode(pil_to_bytes(image)).decode("ascii")
        inputs["strength"] = 0.65
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{quote(account_id, safe='')}/ai/run/@cf/bytedance/stable-diffusion-xl-lightning",
        headers={"Authorization": f"Bearer {token}"},
        json=inputs,
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    image_data = payload.get("result", {}).get("image")
    if not image_data:
        raise RuntimeError("Cloudflare Workers AI returned no image.")
    return image_from_bytes(base64.b64decode(image_data))


def generate_with_ai_horde(api_key, prompt, aspect_ratio=None):
    width, height = {
        "1:1": (1024, 1024),
        "3:2": (960, 640),
        "4:3": (960, 720),
        "9:16": (576, 1024),
        "16:9": (1024, 576),
    }.get(aspect_ratio, (1024, 1024))
    headers = {
        "apikey": api_key,
        "Client-Agent": "KUYILAEEEE-Streamlit:1.0",
    }
    queued = requests.post(
        "https://aihorde.net/api/v2/generate/async",
        headers=headers,
        json={
            "prompt": prompt,
            "params": {
                "width": width,
                "height": height,
                "steps": 20,
                "n": 1,
            },
            "models": ["stable_diffusion"],
        },
        timeout=30,
    )
    queued.raise_for_status()
    job_id = queued.json().get("id")
    if not job_id:
        raise RuntimeError("AI Horde did not return a generation job ID.")

    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        status_response = requests.get(
            f"https://aihorde.net/api/v2/generate/status/{quote(job_id, safe='')}",
            headers=headers,
            timeout=30,
        )
        status_response.raise_for_status()
        payload = status_response.json()
        if payload.get("faulted"):
            raise RuntimeError("AI Horde could not complete the generation.")
        if payload.get("done"):
            generations = payload.get("generations") or []
            if not generations or not generations[0].get("img"):
                raise RuntimeError("AI Horde completed without returning an image.")
            image_result = generations[0]["img"]
            if image_result.startswith("data:image/"):
                return image_from_bytes(
                    base64.b64decode(image_result.split(",", maxsplit=1)[1])
                )
            if image_result.startswith("http"):
                image_response = requests.get(image_result, timeout=60)
                return image_from_api_response(image_response)
            return image_from_bytes(base64.b64decode(image_result))
        time.sleep(3)
    raise TimeoutError("AI Horde image generation timed out. Try again or another provider.")


def generate_with_nvidia(api_key, prompt, aspect_ratio=None):
    width, height = {
        "1:1": (1024, 1024),
        "3:2": (1024, 682),
        "4:3": (1024, 768),
        "9:16": (576, 1024),
        "16:9": (1024, 576),
    }.get(aspect_ratio, (1024, 1024))
    response = requests.post(
        "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        json={
            "text_prompts": [{"text": prompt}],
            "width": width,
            "height": height,
            "steps": 30,
        },
        timeout=180,
    )
    response.raise_for_status()
    artifacts = response.json().get("artifacts") or []
    if not artifacts or not artifacts[0].get("base64"):
        raise RuntimeError("NVIDIA NIM returned no image.")
    return image_from_bytes(base64.b64decode(artifacts[0]["base64"]))


class ImageProviderError(RuntimeError):
    pass


def generate_image(
    model,
    prompt,
    image=None,
    aspect_ratio=None,
    gemini_key="",
    pollinations_key="",
    huggingface_key="",
    cloudflare_token="",
    cloudflare_account_id="",
    ai_horde_key="",
    nvidia_key="",
):
    providers = []
    if gemini_key.strip():
        providers.append(
            (
                "Gemini",
                lambda: generate_with_gemini(
                    genai.Client(api_key=gemini_key.strip()),
                    model,
                    prompt,
                    image=image,
                    aspect_ratio=aspect_ratio,
                ),
            )
        )
    if pollinations_key.strip():
        providers.append(
            (
                "Pollinations AI",
                lambda: generate_with_pollinations(
                    pollinations_key.strip(),
                    "tongyi-mai/z-image-turbo",
                    prompt,
                    image=image,
                    aspect_ratio=aspect_ratio,
                ),
            )
        )
    if huggingface_key.strip() and image is None:
        providers.append(
            (
                "Hugging Face",
                lambda: generate_with_huggingface(
                    huggingface_key.strip(), prompt, aspect_ratio=aspect_ratio
                ),
            )
        )
    if cloudflare_token.strip() and cloudflare_account_id.strip():
        providers.append(
            (
                "Cloudflare Workers AI",
                lambda: generate_with_cloudflare(
                    cloudflare_token.strip(),
                    cloudflare_account_id.strip(),
                    prompt,
                    image=image,
                    aspect_ratio=aspect_ratio,
                ),
            )
        )
    if ai_horde_key.strip() and image is None:
        providers.append(
            (
                "AI Horde",
                lambda: generate_with_ai_horde(
                    ai_horde_key.strip(), prompt, aspect_ratio=aspect_ratio
                ),
            )
        )
    if nvidia_key.strip() and image is None:
        providers.append(
            (
                "NVIDIA NIM",
                lambda: generate_with_nvidia(
                    nvidia_key.strip(), prompt, aspect_ratio=aspect_ratio
                ),
            )
        )

    if not providers:
        if image is not None:
            raise ImageProviderError(
                "The configured providers support text-to-image only. Add Gemini, "
                "Pollinations, or Cloudflare credentials for image editing."
            )
        raise ImageProviderError(
            "Add at least one image provider API key in the sidebar to generate images."
        )

    failures = []
    for provider_name, generate in providers:
        try:
            return generate(), provider_name
        except Exception as exc:
            if isinstance(exc, errors.APIError) and exc.code == 429:
                reason = "quota/rate limit reached"
            elif isinstance(exc, errors.APIError) and exc.code in (401, 403):
                reason = "API key or model access rejected"
            elif isinstance(exc, requests.HTTPError) and exc.response is not None:
                reason = f"HTTP {exc.response.status_code}: {exc.response.text[:240]}"
            else:
                reason = str(exc) or type(exc).__name__
            failures.append(f"{provider_name}: {reason}")

    raise ImageProviderError(
        "All configured image providers failed:\n"
        + "\n".join(failures)
        + "\nCheck provider keys, model access, quota, and billing."
    )


def image_to_text(client, model, image, prompt):
    response = client.models.generate_content(model=model, contents=[prompt, image])
    if not response.text:
        raise RuntimeError("The model returned no text. Try a different task or image.")
    return response.text


def show_api_error(operation, exc):
    if exc.code == 429:
        st.error(
            f"{operation} failed because the Gemini API project has reached its quota "
            "or request limit. This is an API quota/billing issue, not an app error. "
            "Check the project's free-tier usage or wait for its quota to reset. "
            "Enabling billing may incur charges."
        )
        st.markdown(
            "[Check Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) "
            " · [View API usage](https://ai.dev/rate-limit)"
        )
    elif exc.code in (401, 403):
        st.error(
            f"{operation} failed because the API key is invalid or its project does not "
            "have access to this model. Check the key and the project's API access."
        )
    else:
        st.error(f"{operation} failed: Gemini API error ({exc.code} {exc.status}): {exc.message}")


for session_key, secret_name, environment_aliases in (
    ("api_key", "GEMINI_API_KEY", ("GOOGLE_API_KEY",)),
    ("pollinations_api_key", "POLLINATIONS_API_KEY", ()),
    ("huggingface_api_key", "HUGGINGFACE_API_KEY", ()),
    ("cloudflare_api_token", "CLOUDFLARE_API_TOKEN", ()),
    ("cloudflare_account_id", "CLOUDFLARE_ACCOUNT_ID", ()),
    ("ai_horde_api_key", "AI_HORDE_API_KEY", ()),
    ("nvidia_api_key", "NVIDIA_API_KEY", ()),
):
    st.session_state.setdefault(
        session_key,
        get_configured_value(secret_name, *environment_aliases),
    )

with st.sidebar:
    st.markdown("## ✨ Studio settings")
    st.caption("Image generation tries free-quota providers in order.")
    with st.expander("Image provider API keys", expanded=True):
        st.text_input(
            "Gemini API Key",
            type="password",
            key="api_key",
            help="Get a key at https://aistudio.google.com/apikey.",
        )
        st.text_input(
            "Pollinations AI API Key",
            type="password",
            key="pollinations_api_key",
            help="Create a key at https://enter.pollinations.ai/keys. Limit its budget to free credits only.",
        )
        st.text_input(
            "Hugging Face API Key",
            type="password",
            key="huggingface_api_key",
            help="Create a token at https://huggingface.co/settings/tokens. Free accounts get limited monthly credits.",
        )
        st.text_input(
            "Cloudflare Workers AI API Token",
            type="password",
            key="cloudflare_api_token",
            help="Use a Cloudflare Workers Free account; Workers AI has a limited free daily allocation.",
        )
        st.text_input(
            "Cloudflare Account ID",
            key="cloudflare_account_id",
            help="Find this in your Cloudflare dashboard.",
        )
        st.text_input(
            "AI Horde API Key",
            type="password",
            key="ai_horde_api_key",
            help="Get a free key at https://aihorde.net/register. AI Horde is community-powered and may queue requests.",
        )
        st.text_input(
            "NVIDIA NIM API Key",
            type="password",
            key="nvidia_api_key",
            help="Get an NVIDIA API Catalog key at https://build.nvidia.com/. Free trial limits apply.",
        )
        st.caption(
            "Fallback order: Gemini → Pollinations → Hugging Face → Cloudflare → "
            "AI Horde → NVIDIA NIM."
        )
        st.caption(
            "Free quotas are limited. Disable billing or cap each key to free credits "
            "in its provider account; the app cannot control provider billing."
        )
    image_model = st.selectbox("Gemini image model", IMAGE_MODELS, index=1)
    text_model = st.selectbox("Vision / text model", TEXT_MODELS, index=0)
    configured_providers = []
    image_keys = get_image_provider_keys()
    if image_keys["gemini_key"]:
        configured_providers.append("Gemini")
    if image_keys["pollinations_key"]:
        configured_providers.append("Pollinations")
    if image_keys["huggingface_key"]:
        configured_providers.append("Hugging Face")
    if image_keys["cloudflare_token"] and image_keys["cloudflare_account_id"]:
        configured_providers.append("Cloudflare Workers AI")
    if image_keys["ai_horde_key"]:
        configured_providers.append("AI Horde")
    if image_keys["nvidia_key"]:
        configured_providers.append("NVIDIA NIM")
    if configured_providers:
        st.success("Image providers ready: " + " → ".join(configured_providers))
    else:
        st.info("Add at least one image-provider API key to generate images.")
    if image_keys["cloudflare_token"] and not image_keys["cloudflare_account_id"]:
        st.warning("Cloudflare Workers AI needs both its API token and account ID.")

tab_gen, tab_edit, tab_ocr = st.tabs(["🎨 Text → Image", "✏️ Edit Image", "📷 Image → Text"])

with tab_gen:
    st.subheader("Create an image")
    st.caption("Describe the scene you imagine. Choose a visual direction and canvas shape.")
    styles = {
        "No extra style": "",
        "Cinematic": "Cinematic lighting, rich atmosphere, art-directed composition.",
        "Product photography": "Premium commercial product photography, crisp studio lighting.",
        "Watercolor": "Expressive watercolor illustration with visible paper texture.",
        "3D illustration": "Polished 3D illustration, soft materials, rounded forms.",
        "Anime": "Detailed anime illustration, expressive characters, vibrant colors.",
    }
    style_name = st.selectbox("Visual style", list(styles), key="gen_style")
    prompt = st.text_area(
        "Prompt",
        height=120,
        placeholder="A cinematic photo of a golden retriever astronaut on Mars...",
        key="gen_prompt",
    )
    ratio = st.selectbox("Aspect ratio", ["Auto", "1:1", "3:2", "4:3", "9:16", "16:9"])
    if st.button("🚀 Generate Image", type="primary", use_container_width=True):
        image_keys = get_image_provider_keys()
        if not has_image_provider(image_keys):
            st.error("Add at least one provider key in the sidebar before generating.")
        elif not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Cooking your image... 🍌"):
                try:
                    styled_prompt = " ".join(
                        value for value in (prompt.strip(), styles[style_name]) if value
                    )
                    generated_image, provider_name = generate_image(
                        image_model,
                        styled_prompt,
                        aspect_ratio=ratio,
                        **image_keys,
                    )
                    st.session_state["gen_img"] = generated_image
                    st.session_state["gen_provider"] = provider_name
                except ImageProviderError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"Image generation failed: {exc}")
    if "gen_img" in st.session_state:
        st.caption("Generated with " + st.session_state.get("gen_provider", "AI image provider"))
        st.image(st.session_state["gen_img"], width="stretch")
        st.download_button(
            "💾 Download",
            data=pil_to_bytes(st.session_state["gen_img"]),
            file_name="generated.png",
            mime="image/png",
        )
        st.caption("Tip: choose “Use latest generated image” in Edit to keep refining it.")

with tab_edit:
    st.subheader("Edit an image")
    st.caption("Upload an image or continue editing your latest creation.")
    col1, col2 = st.columns(2)
    with col1:
        src = None
        edit_sources = ["Upload an image"]
        if "gen_img" in st.session_state:
            edit_sources.append("Use latest generated image")
        edit_source = st.radio("Image source", edit_sources, horizontal=True)
        if edit_source == "Use latest generated image":
            src = st.session_state["gen_img"]
            st.image(src, caption="Latest generated image", width="stretch")
        else:
            uploaded = st.file_uploader(
                "Upload image", type=["png", "jpg", "jpeg", "webp"], key="edit_upload"
            )
            if uploaded:
                try:
                    src = load_image(uploaded)
                    st.image(src, caption="Original", width="stretch")
                except ValueError as exc:
                    st.error(str(exc))
    with col2:
        instruction = st.text_area(
            "Edit instruction",
            height=120,
            placeholder='Replace the text "SALE" with "MEGA SALE", keep the design identical...',
        )
        if st.button("✨ Apply Edit", type="primary", use_container_width=True):
            image_keys = get_image_provider_keys()
            if not has_image_provider(image_keys):
                st.error("Add at least one provider key in the sidebar before editing.")
            elif src is None:
                st.warning("Please upload a valid image.")
            elif not instruction.strip():
                st.warning("Please describe the edit you want.")
            else:
                with st.spinner("Editing your image... ✨"):
                    try:
                        edited_image, provider_name = generate_image(
                            image_model,
                            instruction,
                            image=src,
                            **image_keys,
                        )
                        st.session_state["edit_img"] = edited_image
                        st.session_state["edit_provider"] = provider_name
                    except ImageProviderError as exc:
                        st.error(str(exc))
                    except Exception as exc:
                        st.error(f"Image editing failed: {exc}")
        if "edit_img" in st.session_state:
            st.caption("Edited with " + st.session_state.get("edit_provider", "AI image provider"))
            st.image(st.session_state["edit_img"], caption="Edited", width="stretch")
            st.download_button(
                "💾 Download",
                data=pil_to_bytes(st.session_state["edit_img"]),
                file_name="edited.png",
                mime="image/png",
            )

with tab_ocr:
    st.subheader("Understand an image")
    st.caption("Extract text, get a description, summarize, or ask a question.")
    col_a, col_b = st.columns(2)
    with col_a:
        uploaded2 = st.file_uploader(
            "Upload image", type=["png", "jpg", "jpeg", "webp"], key="ocr_upload"
        )
        src2 = None
        if uploaded2:
            try:
                src2 = load_image(uploaded2)
                st.image(src2, width="stretch")
            except ValueError as exc:
                st.error(str(exc))
    with col_b:
        task = st.selectbox(
            "Task",
            [
                "Extract ALL text from this image exactly as written",
                "Describe this image in detail",
                "Summarize the key information in this image",
                "Answer my question about this image (type it below)",
            ],
        )
        question = st.text_input("Your question") if task.startswith("Answer") else ""
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            client = get_client()
            if not client:
                st.error("Add your Gemini API key in the sidebar first.")
            elif src2 is None:
                st.warning("Please upload a valid image.")
            elif task.startswith("Answer") and not question.strip():
                st.warning("Please enter your question.")
            else:
                with st.spinner("Reading the image... 🔍"):
                    try:
                        task_prompt = f"{task}. {question}".strip()
                        st.session_state["ocr_result"] = image_to_text(
                            client, text_model, src2, task_prompt
                        )
                    except errors.APIError as exc:
                        show_api_error("Image analysis", exc)
                    except Exception as exc:
                        st.error(f"Image analysis failed: {exc}")
        if "ocr_result" in st.session_state:
            st.text_area("Result", st.session_state["ocr_result"], height=300)
            st.download_button(
                "💾 Download as .txt",
                data=st.session_state["ocr_result"].encode("utf-8"),
                file_name="extracted_text.txt",
                mime="text/plain",
            )
