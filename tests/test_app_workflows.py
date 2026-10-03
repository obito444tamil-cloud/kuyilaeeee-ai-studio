import base64
import os
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from google.genai import errors
from PIL import Image
from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).resolve().parents[1] / "nano_banana_app.py"


def png_bytes():
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "blue").save(buffer, format="PNG")
    return buffer.getvalue()


def gemini_image_response(image_data):
    encoded = base64.b64encode(image_data).decode("ascii")
    return SimpleNamespace(output_image=SimpleNamespace(data=encoded))


def http_image_response(image_data):
    return SimpleNamespace(
        content=image_data,
        headers={"content-type": "image/png"},
        raise_for_status=Mock(),
    )


def json_image_response(payload):
    return SimpleNamespace(
        content=b"",
        headers={"content-type": "application/json"},
        raise_for_status=Mock(),
        json=Mock(return_value=payload),
    )


class AppWorkflowTests(unittest.TestCase):
    def empty_provider_environment(self):
        return patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "",
                "GOOGLE_API_KEY": "",
                "POLLINATIONS_API_KEY": "",
                "HUGGINGFACE_API_KEY": "",
                "CLOUDFLARE_API_TOKEN": "",
                "CLOUDFLARE_ACCOUNT_ID": "",
                "AI_HORDE_API_KEY": "",
                "NVIDIA_API_KEY": "",
            },
        )

    def test_image_generation_editing_and_image_analysis(self):
        image_data = png_bytes()
        text_response = SimpleNamespace(text="Extracted sample text", parts=[])
        client = SimpleNamespace(
            interactions=SimpleNamespace(
                create=Mock(
                    side_effect=[
                        gemini_image_response(image_data),
                        gemini_image_response(image_data),
                    ]
                )
            ),
            models=SimpleNamespace(generate_content=Mock(return_value=text_response)),
        )

        with self.empty_provider_environment():
            with patch("google.genai.Client", return_value=client):
                app = AppTest.from_file(str(APP_FILE)).run()
                app.sidebar.text_input(key="api_key").set_value("test-key").run()

                app.text_area(key="gen_prompt").set_value("A simple blue square").run()
                app.button[0].click().run()
                self.assertIsInstance(app.session_state["gen_img"], Image.Image)

                app.file_uploader(key="edit_upload").upload(
                    "source.png", image_data, "image/png"
                ).run()
                app.text_area[1].set_value("Make the square red").run()
                app.button[1].click().run()
                self.assertIsInstance(app.session_state["edit_img"], Image.Image)

                app.file_uploader(key="ocr_upload").upload(
                    "text.png", image_data, "image/png"
                ).run()
                app.button[2].click().run()
                self.assertEqual(
                    app.session_state["ocr_result"], "Extracted sample text"
                )

        self.assertFalse(app.exception)
        self.assertEqual(client.interactions.create.call_count, 2)
        self.assertEqual(client.models.generate_content.call_count, 1)

    def test_requests_provider_key_before_calling_any_api(self):
        with self.empty_provider_environment():
            with patch("google.genai.Client") as create_client:
                app = AppTest.from_file(str(APP_FILE)).run()
                app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertIn("at least one provider key", app.error[0].value)
        create_client.assert_not_called()

    def test_quota_error_is_reported_when_no_fallback_is_configured(self):
        client = SimpleNamespace(
            interactions=SimpleNamespace(
                create=Mock(
                    side_effect=errors.ClientError(
                        429,
                        {
                            "error": {
                                "code": 429,
                                "status": "RESOURCE_EXHAUSTED",
                                "message": "Quota exceeded.",
                            }
                        },
                    )
                )
            ),
            models=SimpleNamespace(generate_content=Mock()),
        )
        with self.empty_provider_environment():
            with patch("google.genai.Client", return_value=client):
                app = AppTest.from_file(str(APP_FILE)).run()
                app.sidebar.text_input(key="api_key").set_value("test-key").run()
                app.text_area(key="gen_prompt").set_value("A blue square").run()
                app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertIn("Gemini: quota/rate limit reached", app.error[0].value)
        self.assertIn("All configured image providers failed", app.error[0].value)

    def test_falls_back_to_pollinations_when_gemini_quota_is_exhausted(self):
        image_data = png_bytes()
        client = SimpleNamespace(
            interactions=SimpleNamespace(
                create=Mock(
                    side_effect=errors.ClientError(
                        429,
                        {
                            "error": {
                                "code": 429,
                                "status": "RESOURCE_EXHAUSTED",
                                "message": "Quota exceeded.",
                            }
                        },
                    )
                )
            ),
            models=SimpleNamespace(generate_content=Mock()),
        )
        with self.empty_provider_environment():
            with patch("google.genai.Client", return_value=client):
                with patch(
                    "requests.get", return_value=http_image_response(image_data)
                ) as get:
                    app = AppTest.from_file(str(APP_FILE)).run()
                    app.sidebar.text_input(key="api_key").set_value("gemini-key").run()
                    app.sidebar.text_input(key="pollinations_api_key").set_value(
                        "pollinations-key"
                    ).run()
                    app.text_area(key="gen_prompt").set_value("A blue square").run()
                    app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertIsInstance(app.session_state["gen_img"], Image.Image)
        self.assertEqual(app.session_state["gen_provider"], "Pollinations AI")
        self.assertEqual(client.interactions.create.call_count, 1)
        self.assertEqual(
            get.call_args.kwargs["headers"]["Authorization"],
            "Bearer pollinations-key",
        )

    def test_huggingface_provider_can_generate_without_gemini_key(self):
        image_data = png_bytes()
        with self.empty_provider_environment():
            with patch(
                "requests.post", return_value=http_image_response(image_data)
            ) as post:
                app = AppTest.from_file(str(APP_FILE)).run()
                app.sidebar.text_input(key="huggingface_api_key").set_value("hf-key").run()
                app.text_area(key="gen_prompt").set_value("A blue square").run()
                app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["gen_provider"], "Hugging Face")
        self.assertIn("router.huggingface.co", post.call_args.args[0])
        self.assertEqual(
            post.call_args.kwargs["headers"]["Authorization"], "Bearer hf-key"
        )

    def test_cloudflare_free_model_can_generate_without_gemini_key(self):
        image_data = png_bytes()
        image_base64 = base64.b64encode(image_data).decode("ascii")
        response = json_image_response({"result": {"image": image_base64}})
        with self.empty_provider_environment():
            with patch("requests.post", return_value=response) as post:
                app = AppTest.from_file(str(APP_FILE)).run()
                app.sidebar.text_input(key="cloudflare_api_token").set_value(
                    "cloudflare-token"
                ).run()
                app.sidebar.text_input(key="cloudflare_account_id").set_value(
                    "account-id"
                ).run()
                app.text_area(key="gen_prompt").set_value("A blue square").run()
                app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["gen_provider"], "Cloudflare Workers AI")
        self.assertIn("/accounts/account-id/ai/run/", post.call_args.args[0])
        self.assertEqual(
            post.call_args.kwargs["headers"]["Authorization"],
            "Bearer cloudflare-token",
        )

    def test_nvidia_trial_api_returns_image_response(self):
        image_data = png_bytes()
        image_base64 = base64.b64encode(image_data).decode("ascii")
        response = json_image_response({"artifacts": [{"base64": image_base64}]})
        with self.empty_provider_environment():
            with patch("requests.post", return_value=response) as post:
                app = AppTest.from_file(str(APP_FILE)).run()
                app.sidebar.text_input(key="nvidia_api_key").set_value("nvidia-key").run()
                app.text_area(key="gen_prompt").set_value("A blue square").run()
                app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["gen_provider"], "NVIDIA NIM")
        self.assertIn("ai.api.nvidia.com", post.call_args.args[0])
        self.assertEqual(
            post.call_args.kwargs["headers"]["Authorization"], "Bearer nvidia-key"
        )

    def test_ai_horde_uses_its_free_async_generation_api(self):
        image_data = png_bytes()
        queued = SimpleNamespace(
            raise_for_status=Mock(),
            json=Mock(return_value={"id": "job-123"}),
        )
        completed = SimpleNamespace(
            raise_for_status=Mock(),
            json=Mock(
                return_value={
                    "done": True,
                    "faulted": False,
                    "generations": [
                        {
                            "img": "data:image/png;base64,"
                            + base64.b64encode(image_data).decode("ascii")
                        }
                    ],
                }
            ),
        )
        with self.empty_provider_environment():
            with patch("requests.post", return_value=queued) as post:
                with patch("requests.get", return_value=completed) as get:
                    app = AppTest.from_file(str(APP_FILE)).run()
                    app.sidebar.text_input(key="ai_horde_api_key").set_value(
                        "horde-key"
                    ).run()
                    app.text_area(key="gen_prompt").set_value("A blue square").run()
                    app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["gen_provider"], "AI Horde")
        self.assertIn("/generate/async", post.call_args.args[0])
        self.assertEqual(post.call_args.kwargs["headers"]["apikey"], "horde-key")
        self.assertIn("/generate/status/job-123", get.call_args.args[0])

    def test_fallback_order_continues_to_huggingface_after_pollinations_failure(self):
        image_data = png_bytes()
        client = SimpleNamespace(
            interactions=SimpleNamespace(
                create=Mock(
                    side_effect=errors.ClientError(
                        429,
                        {
                            "error": {
                                "code": 429,
                                "status": "RESOURCE_EXHAUSTED",
                                "message": "Quota exceeded.",
                            }
                        },
                    )
                )
            ),
            models=SimpleNamespace(generate_content=Mock()),
        )
        pollinations_failure = SimpleNamespace(
            headers={"content-type": "application/json"},
            raise_for_status=Mock(
                side_effect=__import__("requests").HTTPError(
                    "Pollinations unavailable",
                    response=SimpleNamespace(status_code=503, text="Unavailable"),
                )
            ),
        )
        with self.empty_provider_environment():
            with patch("google.genai.Client", return_value=client):
                with patch("requests.get", return_value=pollinations_failure):
                    with patch(
                        "requests.post", return_value=http_image_response(image_data)
                    ) as post:
                        app = AppTest.from_file(str(APP_FILE)).run()
                        app.sidebar.text_input(key="api_key").set_value("gemini-key").run()
                        app.sidebar.text_input(key="pollinations_api_key").set_value(
                            "pollinations-key"
                        ).run()
                        app.sidebar.text_input(key="huggingface_api_key").set_value(
                            "hf-key"
                        ).run()
                        app.text_area(key="gen_prompt").set_value("A blue square").run()
                        app.button[0].click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["gen_provider"], "Hugging Face")
        self.assertEqual(client.interactions.create.call_count, 1)
        self.assertEqual(post.call_count, 1)
        self.assertIn("router.huggingface.co", post.call_args.args[0])

    def test_six_provider_slots_are_available(self):
        with self.empty_provider_environment():
            app = AppTest.from_file(str(APP_FILE)).run()

        expected_keys = {
            "api_key",
            "pollinations_api_key",
            "huggingface_api_key",
            "cloudflare_api_token",
            "ai_horde_api_key",
            "nvidia_api_key",
        }
        visible_keys = {widget.key for widget in app.sidebar.text_input}
        self.assertTrue(expected_keys.issubset(visible_keys))
        self.assertFalse(app.exception)

    def test_style_preset_and_generated_image_can_be_edited(self):
        image_data = png_bytes()
        client = SimpleNamespace(
            interactions=SimpleNamespace(
                create=Mock(
                    side_effect=[
                        gemini_image_response(image_data),
                        gemini_image_response(image_data),
                    ]
                )
            ),
            models=SimpleNamespace(generate_content=Mock()),
        )

        with self.empty_provider_environment():
            with patch("google.genai.Client", return_value=client):
                app = AppTest.from_file(str(APP_FILE)).run()
                app.sidebar.text_input(key="api_key").set_value("test-key").run()
                app.selectbox(key="gen_style").set_value("Cinematic").run()
                app.text_area(key="gen_prompt").set_value("A quiet mountain lake").run()
                app.button[0].click().run()
                app.radio[0].set_value("Use latest generated image").run()
                app.text_area[1].set_value("Add a small wooden boat").run()
                app.button[1].click().run()

        self.assertFalse(app.exception)
        self.assertIsInstance(app.session_state["edit_img"], Image.Image)
        generation_request = client.interactions.create.call_args_list[0].kwargs
        self.assertIn("Cinematic lighting", generation_request["input"][0]["text"])
        edit_request = client.interactions.create.call_args_list[1].kwargs
        self.assertEqual(edit_request["input"][0]["text"], "Add a small wooden boat")
        self.assertEqual(edit_request["input"][1]["type"], "image")


if __name__ == "__main__":
    unittest.main()
