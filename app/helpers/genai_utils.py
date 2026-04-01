import os
import random
import re
import time

import requests

from .logging_utils import get_logger, safe_log_text

REQUIRED_SECTIONS = [
    "Profile Summary (About)",
    "Headline",
    "Experience",
    "Skills",
    "Education",
    "Projects",
    "Certifications",
    "Awards & Accomplishments",
    "Courses",
    "Publications",
    "Licenses",
    "Volunteering",
    "Organizations",
    "Recommendations",
    "Languages",
    "Personal Interests",
    "Any Other Relevant Section",
]

logger = get_logger(__name__)


def is_output_complete(text):
    """Checks if all required section headers are present in the AI response."""
    found = 0
    for sec in REQUIRED_SECTIONS:
        pattern = rf"(?i)###\s*{re.escape(sec)}"
        if re.search(pattern, text):
            found += 1
    return found == len(REQUIRED_SECTIONS)


def call_gemini_with_retries(prompt):
    """
    Sends the prompt to Gemini API with network retries and output completeness validation.
    Returns the generated text or an error message.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning(
            "GEMINI_API_KEY is not set; Gemini requests will fail until configured."
        )
        return (
            "Error: Gemini API key not set. Set GEMINI_API_KEY in your environment or .env file."
        )

    def send_request(prompt_text, max_api_retries=4):
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
        candidate_endpoints = [
            (
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
                "gemini-2.5-pro",
            ),
            (
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                "gemini-2.5-flash",
            ),
        ]
        last_error = None

        for attempt_index in range(max_api_retries):
            for ep, model_name in candidate_endpoints:
                try:
                    response = requests.post(
                        ep,
                        json=payload,
                        headers=headers,
                        timeout=60,
                    )
                    if response.status_code in {429, 500, 502, 503, 504}:
                        last_error = requests.HTTPError(
                            f"HTTP {response.status_code} {response.reason}"
                        )
                        continue
                    response.raise_for_status()
                    logger.info(
                        "Gemini response generated with model %s",
                        safe_log_text(model_name),
                    )
                    return response.json()
                except (requests.Timeout, requests.ConnectionError) as e:
                    last_error = e
                    continue

            sleep_seconds = min(2 ** attempt_index + random.uniform(0, 0.5), 10)
            try:
                time.sleep(sleep_seconds)
            except Exception:
                pass

        if last_error:
            raise last_error
        raise Exception("Failed to get response after retries.")

    tries = 0
    max_tries = 2
    last_response = None
    current_prompt = prompt

    while tries < max_tries:
        try:
            data = send_request(current_prompt)

            candidates = data.get("candidates", [])
            if not candidates or not candidates[0].get("content"):
                return "Error: Gemini API returned an unexpected or empty response."

            parts = candidates[0]["content"].get("parts", [])
            text = parts[0].get("text", "").strip() if parts else ""

            if not text:
                return "Error: Gemini API returned an incomplete or blank response."

            last_response = text

            if is_output_complete(text):
                return text

            tries += 1
            retry_notice = (
                "\n\nSYSTEM NOTICE: Your last response was incomplete. "
                "Please output ALL 17 sections, with all required parts and fields as per the prompt format."
            )
            current_prompt += retry_notice

        except (requests.Timeout, requests.ConnectionError):
            tries += 1
            continue
        except requests.HTTPError as http_err:
            return (
                "Error: Service temporarily unavailable from Gemini API. "
                "Please try again shortly. Details: " + safe_log_text(http_err)
            )
        except Exception as e:
            return f"Error: {safe_log_text(e)}"

    return last_response or "Error: Gemini API did not return a usable response."
