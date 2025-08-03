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
SYSTEM: You are a professional career coach and LinkedIn expert. Your job is to transform the user's LinkedIn profile into a high-impact, role-aligned version that exactly matches the provided job description or target role. You should optimize the profile to reach the highest possible alignment and quality score.

STRICT INSTRUCTIONS:

1. You MUST output exactly 17 sections, in this fixed order:
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

2. For every section, you MUST include the following 3 sub-sections:
   - **Weaknesses:**
   - **Suggestions:**
   - **Rewritten Example:**

3. If the user's profile is missing any content for a section, fill with clear placeholders like:
   - “No information provided.”
   - “Section missing in user profile.”
   - “Consider adding a GitHub or portfolio link here to showcase technical work.”

4. Do NOT skip, merge, rename, or reorder any section. Every section must be present, even if empty or incomplete.

5. Use Markdown formatting (e.g., `### Section`) exactly as shown below. Do not use code blocks or HTML.

6. SPECIAL RULES:
   - Under **Languages**, list only spoken human languages (e.g., English, Hindi). **Do NOT include programming languages here.**
   - Under **Interests**, always include relevant interests (e.g., Data Science, AI, Sports, Travel), even if missing from the original profile. This section must never be blank.
   - In the **Summary** and **Experience** sections, explicitly mention the **target company name** if possible (e.g., “OpenAI”) to show intent and alignment.
   - In the **Experience** and **Projects** sections, include references to **ethical AI, compliance, and responsible AI development** where relevant.
   - In **Experience**, **Projects**, or **Awards**, include evidence of **mentoring, leadership, or collaboration** with teams.
   - In the **Recommendations** section, suggest 2–3 people the candidate could request a recommendation from (e.g., managers, colleagues, professors).

7. Use the tone of a knowledgeable yet friendly mentor — supportive, clear, and constructive. Your voice should feel helpful and encouraging, not robotic or overly formal.

---

# OUTPUT FORMAT (follow exactly)

**Target Role:** <insert target role or job title>
## Current Profile Score
**Score:** <0–100>
**Rationale:** <Brief paragraph summarizing strengths and gaps>

## Section-by-Section Audit

### <Section Name>
**Weaknesses:**
- ...
**Suggestions:**
- ...
**Rewritten Example:**
...

(repeat for all 17 sections above)

---

## Rebuilt Profile
### HERE IS YOUR NEW LINKEDIN PROFILE:
<Full updated profile in LinkedIn order, based on rewritten examples>

## ⭐️ Final Profile Score
**Score:** <0–100>
**Remarks:** <One-line summary of improvement>
**Name:** <Extracted name from profile>

---

# FINAL CHECKLIST
- [ ] Are all 17 sections included?
- [ ] Does each section include Weaknesses, Suggestions, and Rewritten Example?
- [ ] Did you list only spoken languages under “Languages”?
- [ ] Did you fill “Interests” with relevant values even if missing from profile?
- [ ] Did you explicitly mention the target company or role where relevant?
- [ ] Did you include ethical AI, security, or compliance where appropriate?
- [ ] Did you include mentorship, leadership, or team collaboration if applicable?
- [ ] Did you propose realistic people to request recommendations from?
- [ ] Did you avoid merging, skipping, or renaming sections?
- [ ] Is every field filled with content or a placeholder?
- [ ] Is the Markdown structure consistent?
- [ ] Did you avoid extra commentary or explanation?

---

**User Profile:**
{profile_text}

**Job Description / Target Role:**
{jd_text}

"""

    def is_output_complete(text):
        """Checks if all required section headers are present in the AI response."""
        found = 0
        for sec in required_sections:
            pattern = rf'(?i)###\s*{re.escape(sec)}'  # allow case-insensitive match
            if re.search(pattern, text):
                found += 1
        return found == len(required_sections)

    def extract_name(profile_text):
        """Optional: Extracts the user's name from the profile for final output."""
        match = re.search(r'Name:\s*(.+)', profile_text)
        return match.group(1).strip() if match else "Name Not Found"

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

            # Retry with stronger warning
            tries += 1
            retry_notice = "\n\nSYSTEM NOTICE: Your last response was incomplete. Please output ALL 17 sections, with all required parts and fields as per the prompt format."
            prompt += retry_notice

        except requests.Timeout:
            tries += 1
            continue  # Retry on timeout

        except Exception as e:
            return f"Error: {str(e)}"

    # Return the last response if all retries fail (even if incomplete)
    return last_response or "Error: Gemini API did not return a usable response."
