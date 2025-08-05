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
        'Recommendations', 'Languages', 'personal Interests', 'Any other relevant section'
    ]

    def build_prompt(profile_text, jd_text):
        return f"""
SYSTEM: You are a professional career coach and LinkedIn optimization expert.

Your task is to:
1. Analyze the user’s provided job description or target role (if only a role is given, infer top-tier expectations for that role).
2. Evaluate the user’s current LinkedIn profile for alignment with this role.
3. Highlight exactly which elements align and which fall short.
4. Provide specific, actionable improvements.
5. Rebuild the profile to a **perfect 100/100 score**, using strict markdown formatting.

---

INPUT CONTEXT:
Job Description or Target Role:
{jd_text}

User LinkedIn Profile:
{profile_text}

---

STRICT INSTRUCTIONS:

1. Output **exactly 17 sections**, in this **fixed order**:
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
   16. Personal Interests  
   17. Any other relevant section

2. For **every section**, include:
   - **Weaknesses:** What’s missing, vague, or misaligned?  
   - **Suggestions:** How to fix or strengthen it.  
   - **Rewritten Example:** A polished, role-aligned version (or high-quality placeholder if empty).

3. **Never** skip, merge, rename, or reorder sections—**all 17** must appear, even if the original profile lacked content.

4. If a section is empty or weak, supply a **realistic placeholder** (e.g., sample GitHub link, mock blog title, portfolio prompt, or a realistic recommendation request).

5. Use **strict Markdown** only:
   - `### Section Name` headers  
   - **Bolded** labels for Weaknesses/Suggestions/Rewritten Example  
   - No HTML, no code blocks, no tables.

---

### SPECIAL SCORING RULES (TO HIT 100/100):

- ✅ Mention the **target company name** (e.g., Google, TCS, Meta) in **Summary** and at least one bullet in **Experience**.  
- ✅ For service-based firms (TCS, Accenture), spotlight **teamwork**, client deliverables, SLAs, and reliability.  
- ✅ Include **2–3 technical projects** with GitHub links and **quantifiable metrics** (accuracy %, performance gains).  
- ✅ Reference **MLflow**, **Weights & Biases**, or equivalent **reproducibility tools** for any ML work.  
- ✅ Call out **ethical AI**, **bias mitigation**, or **responsible AI** in relevant projects.  
- ✅ Add at least **one professional certification** (Coursera, Google, AWS, etc.).  
- ✅ If **Publications** is empty, create a **realistic blog/article placeholder**.  
- ✅ List **only spoken languages** under “Languages” (no coding languages).  
- ✅ If **Volunteering** is empty, create a **realistic volunteer placeholder**.
- ✅ “Personal Interests” must be a meaningful list (AI, Data, Startups, Open Source, Travel, etc.).  
- ✅ In “Any other relevant section,” include **GitHub**, **portfolio**, or **personal website** (use placeholders if needed).

---

# OUTPUT FORMAT

**Target Role:** <role>  
**Target Company:** <company>

## Current Profile Score  
**Score:** <0–100>  
**Rationale:** <Brief summary of strengths & gaps>

## Section-by-Section Audit

### Profile Summary (About)  
**Weaknesses:**  
…  
**Suggestions:**  
…  
**Rewritten Example:**  
…

*(Repeat exactly for all 17 sections.)*

---

## Rebuilt Profile  
### HERE IS YOUR NEW LINKEDIN PROFILE:  
<Full 17-section profile built from the above “Rewritten Example” entries>

---

## ⭐️ Final Profile Score  
**Score:** <0–100>  
**Remarks:** <One-line summary of alignment>  
**Name:** <Extracted full name>

---

# FINAL CHECKLIST (for the AI)

- [ ] All 17 sections present and in the correct order  
- [ ] Each has **Weaknesses**, **Suggestions**, **Rewritten Example**  
- [ ] Only spoken languages in “Languages”  
- [ ] “Personal Interests” meaningfully filled  
- [ ] Target company mentioned in Summary & Experience  z
- [ ] At least one certification included  
- [ ] Ethical AI or responsible practices noted if relevant  
- [ ] GitHub/portfolio link in “Any other relevant section”  
- [ ] Placeholder publication added if needed  
- [ ] Strict Markdown formatting throughout  

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
