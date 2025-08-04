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
SYSTEM: You are a professional career coach and LinkedIn expert. Your task is to:
1. Carefully analyze the provided job description/requirements.
2. Transform the user's LinkedIn profile to perfectly align with these requirements.
3. Highlight relevant experience and skills that match the job requirements.
4. Suggest improvements where the profile doesn't meet the requirements.

INPUT CONTEXT:
Job Description/Target Role:
{jd_text}

User Profile:
{profile_text}

---

STRICT INSTRUCTIONS:

1. You MUST output **exactly 17 sections**, in this fixed order:
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

2. For EVERY section, you MUST include these three clearly labeled sub-sections:
   - **Weaknesses:**
   - **Suggestions:**
   - **Rewritten Example:**

3. If any section has no content in the original profile, provide a meaningful placeholder like:
   - “No information provided.”
   - “Section missing in user profile.”
   - “Consider adding a GitHub or portfolio link here.”

4. DO NOT skip, merge, rename, or reorder sections — even if content is missing.

5. Format your entire output in **Markdown**, exactly like:
<Section Name>  
**Weaknesses:**  
...  
**Suggestions:**  
...  
**Rewritten Example:**  
...

6. SPECIAL GUIDELINES:
- Under **Languages**, include only spoken languages. (Do NOT include programming languages.)
- Under **Personal Interests**, ALWAYS list relevant interests like AI, Tech, Travel, etc. This section must NOT be blank.
- Explicitly mention the **target company name** (e.g., Google) in the Summary or Experience.
- Mention **ethical AI**, **fairness**, or **responsible AI** practices where relevant.
- Include references to **mentorship, leadership, or teamwork** where applicable.
- In **Recommendations**, suggest 2–3 specific people (e.g., professors, mentors, managers).
- In **Projects**, include at least two GitHub repository links.
- In **Certifications**, include one from Google or Coursera if missing.
- In **Publications**, add at least one blog-style placeholder article.
- In **Any other relevant section**, always include a GitHub or portfolio link.
- Mention any use of **MLflow**, **Weights & Biases**, or version control for reproducibility.

7. Use a warm, friendly, and clear tone — like a helpful mentor, not a robot.

---

# OUTPUT FORMAT (follow exactly)

**Target Role:** <Job Title or Target Role>  
## Current Profile Score  
**Score:** <0–100>  
**Rationale:** <Brief paragraph summarizing strengths and gaps>

## Section-by-Section Audit

### Profile Summary (About)  
**Weaknesses:**  
...  
**Suggestions:**  
...  
**Rewritten Example:**  
...

(repeat for all 17 sections...)

---

## Rebuilt Profile  
### HERE IS YOUR NEW LINKEDIN PROFILE:  
<Full updated profile in LinkedIn order, based on rewritten examples>

## ⭐️ Final Profile Score  
**Score:** <0–100>  
**Remarks:** Perfectly aligned with the target role and fully rebuilt  
**Name:** <Extracted from profile>

---

# FINAL CHECKLIST
- [x] All 17 sections included?
- [x] Each section includes Weaknesses, Suggestions, and Rewritten Example?
- [x] Spoken languages only under “Languages”?
- [x] “Personal Interests” filled with relevant values?
- [x] Target company mentioned where relevant?
- [x] Ethical AI, fairness, or compliance mentioned?
- [x] Mentorship, leadership, or teamwork mentioned?
- [x] Realistic recommendations suggested?
- [x] Project GitHub links added?
- [x] At least one ML certification included?
- [x] At least one publication or blog placeholder added?
- [x] GitHub/portfolio in “Any other relevant section”?
- [x] Reproducibility tools (MLflow/W&B) mentioned?
- [x] No sections skipped, merged, or renamed?
- [x] Every field filled with content or placeholder?
- [x] Markdown structure consistent?
- [x] No extra commentary?


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
