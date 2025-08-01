
import os
import requests
import re

def analyze_profile(profile_text, jd_text):
    """
    Calls Gemini API to analyze and rewrite a LinkedIn profile for a target job/role.
    Returns the AI's markdown response or an error message.
    Ensures all required sections are present; retries once if not.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return 'Gemini API key not set.'

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    required_sections = [
        'Profile Summary (About)', 'Headline', 'Experience', 'Skills', 'Education', 'Projects', 'Certifications',
        'Awards & Accomplishments', 'Courses', 'Publications', 'Licenses', 'Volunteering', 'Organizations',
        'Recommendations', 'Languages', 'Interests', 'Any other relevant section'
    ]
    
    def build_prompt(profile_text, jd_text):
        return f"""
SYSTEM: You are an expert LinkedIn coach and career mentor. Your job is to take the user's exported LinkedIn profile and transform it into a high-impact, role-focused version that is as closely aligned as possible to the provided job description or target role. You must output a complete, production-ready analysis and rewrite, following the exact structure below.

STRICT INSTRUCTIONS:

- You MUST output ALL 17 required sections, in the exact order and format below.
- For EVERY section, ALWAYS provide all three labeled parts: **Weaknesses:**, **Suggestions:**, and **Rewritten Example:**.
- If any content is missing or not available, you MUST fill it with a clear placeholder (e.g., "No information provided." or "Section missing in user profile.").
- NEVER skip, merge, or omit any section, even if the user's profile is missing that section.
- NEVER leave any field blank or empty. Every field must have a meaningful value or a placeholder.
- Use Markdown formatting as shown below. Do not use code blocks or HTML.
- Output must be parseable and consistent. Do not add extra commentary or deviate from the format.
- give spoken Languages only under Languages section.
- give Interests always.

---

# OUTPUT FORMAT (follow exactly)

**Target Role:** <the role you are optimizing for>
## Current Profile Score
**Score:** <0-100>
**Rationale:** <2-3 sentences explaining strengths and gaps>

## Section-by-Section Audit
For each section below, output:
### <Section Name>
**Weaknesses:**
- ...
**Suggestions:**
- ...
**Rewritten Example:**
<rewritten content>

Sections to cover (in this order):
1. Profile Summary (About)
2. Headline
3. Experience
4. Skills
5. Education
6. Projects
7. Certifications
8. Awards & Accomplishments
9. Courses
10. Publications
11. Licenses
12. Volunteering
13. Organizations
14. Recommendations
15. Languages
16. Interests
17. Any other relevant section

## Rebuilt Profile
### HERE IS YOUR NEW LINKEDIN PROFILE:
<full updated profile, in LinkedIn order, based on the rewritten examples above>

## ⭐️ Final Profile Score
**Score:** <0-100>
**Remarks:** <one short line summarizing how the profile improved>
**Name:** <extract the full name from the profile>

---

# FINAL CHECKLIST (for the AI)
- [ ] Did you output ALL 17 required sections, in the correct order?
- [ ] Did you fill every field, even if with a placeholder?
- [ ] Did you use the exact Markdown structure above?
- [ ] Did you avoid extra commentary or code blocks?

---

**User Profile:**
{profile_text}

**Job Description / Target Role:**
{jd_text}
"""

    def is_output_complete(text):
        # Check for all 17 required section headings
        found = 0
        for sec in required_sections:
            # Accept some flexibility in section heading formatting
            if re.search(rf'###\s*{re.escape(sec)}', text, re.IGNORECASE):
                found += 1
        return found == 17

    prompt = build_prompt(profile_text, jd_text)
    tries = 0
    max_tries = 2
    last_response = None
    while tries < max_tries:
        try:
            response = requests.post(
                endpoint,
                json={ "contents": [ { "parts": [ { "text": prompt } ] } ] },
                headers={ "Content-Type": "application/json", "X-goog-api-key": api_key },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates")
            if not candidates or not candidates[0].get("content"):
                return "Error: Gemini API returned an unexpected response."
            parts = candidates[0]["content"].get("parts")
            if not parts or not parts[0].get("text"):
                return "Error: Gemini API returned an incomplete response."
            text = parts[0]["text"]
            last_response = text
            if is_output_complete(text):
                return text
            tries += 1
            # If incomplete, retry with a warning preamble
            prompt = "SYSTEM: Your last response was incomplete. Please output ALL 17 sections, with all fields, as per the instructions.\n\n" + prompt
        except requests.Timeout:
            return "Error: Gemini API request timed out."
        except Exception as e:
            return f"Error: {e}"
    # If still incomplete, return the last response (will be parsed with placeholders)
    return last_response or "Error: Gemini API did not return a usable response."
