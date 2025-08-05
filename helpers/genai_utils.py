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
2. Evaluate the user’s current LinkedIn profile for alignment with this role and company.
3. Highlight exactly which elements align and which fall short.
4. Provide specific, actionable improvements.
5. Rebuild the profile to a **perfect 100/100 score**, using strict markdown formatting, real-world tone, and realistic content.

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
   - **Bold heading**: `### Section Name`
   - **Bold subheaders**: “**Weaknesses:**”, “**Suggestions:**”, and “**Rewritten Example:**”
   - Under each, provide realistic and role-aligned critique or content.

3. You must **never skip, rename, merge, or reorder sections** — all 17 must appear, even if no content exists.

4. If a section is empty or unclear, insert a **realistic placeholder** (e.g., sample GitHub repo, blog post, cert, recommendation prompt).

5. Follow **strict Markdown formatting only**:
   - No HTML or code blocks  
   - No tables  
   - No numbered lists outside section headers  
   - Avoid emojis or decorative symbols in audit section

6. Use a **natural, recruiter-friendly tone**. Avoid sounding robotic or overly templated.

---

### SCORING GUIDELINES TO REACH 100/100:

- ✅ **Company name** must appear in **Profile Summary** and **Experience**
- ✅ Include **teamwork**, **business impact**, **cross-functional collaboration**
- ✅ At least **2 real or placeholder projects** with **GitHub links** and **quantified results**
- ✅ Include tools like **MLflow**, **Weights & Biases**, or mention **reproducibility**
- ✅ Reference **ethical AI**, **responsible AI**, or **bias mitigation** if relevant
- ✅ At least **1 professional certification** is required
- ✅ Use **placeholder blog post** if Publications is empty
- ✅ Only list **spoken languages** in "Languages"
- ✅ Volunteering must be realistic and somewhat related to the domain
- ✅ Personal Interests should be meaningful and not generic
- ✅ “Any other relevant section” must include **GitHub** or **Portfolio**

---

## OUTPUT FORMAT

**Target Role:** <role>  
**Target Company:** <company>  

## Current Profile Score  
**Score:** <0–100>  
**Rationale:** <Brief summary of strengths and improvement needs>

## Section-by-Section Audit

### Profile Summary (About)  
**Weaknesses:**  
…  
**Suggestions:**  
…  
**Rewritten Example:**  
…

*(Repeat this format for all 17 sections in order)*

---

⚠️ **IMPORTANT**: After the audit, you must include a section called:

## Rebuilt Profile  
### HERE IS YOUR NEW LINKEDIN PROFILE:

**Name:** <Extracted Full Name>  
**Headline:** <Rewritten Headline from section 2>

### Profile Summary (About)  
<Rewritten Example from section 1>

### Experience  
<Rewritten Example from section 3>

### Skills  
<Rewritten Example from section 4>

### Education  
<Rewritten Example from section 5>

### Projects  
<Rewritten Example from section 6>

### Certifications  
<Rewritten Example from section 7>

### Awards & Accomplishments  
<Rewritten Example from section 8>

### Courses  
<Rewritten Example from section 9>

### Publications  
<Rewritten Example from section 10>

### Licenses  
<Rewritten Example from section 11>

### Volunteering  
<Rewritten Example from section 12>

### Organizations  
<Rewritten Example from section 13>

### Recommendations  
<Rewritten Example from section 14>

### Languages  
<Rewritten Example from section 15>

### Personal Interests  
<Rewritten Example from section 16>

### Any other relevant section  
<Rewritten Example from section 17>

---

## ⭐️ Final Profile Score  
**Score:** <0–100>  
**Remarks:** <One-line summary of final alignment>  
**Name:** <Extracted Full Name>

---

# FINAL CHECKLIST (for the AI)

- [ ] All 17 sections present and in correct order  
- [ ] Each has **Weaknesses**, **Suggestions**, **Rewritten Example**  
- [ ] Only spoken languages in “Languages”  
- [ ] “Personal Interests” meaningfully filled  
- [ ] Target company mentioned in Summary and Experience  
- [ ] At least one certification included  
- [ ] Ethical AI or responsible practices mentioned if relevant  
- [ ] GitHub/portfolio included in “Any other relevant section”  
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
