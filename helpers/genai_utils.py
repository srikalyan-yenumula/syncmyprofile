import os
import requests
import re
import time
import random

def analyze_profile(profile_text, jd_text, extra_sections=None):
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
        'Recommendations', 'Languages', 'Personal Interests', 'Any Other Relevant Section'
    ]

    def build_prompt(profile_text, jd_text, extra_sections=None):
        # Always include both blocks, even if extra_sections is empty or None
        extra_block = (
            f"\n--- BEGIN USER-PASTED EXTRA SECTIONS ---\n"
            f"{extra_sections if extra_sections is not None else ''}\n"
            f"--- END USER-PASTED EXTRA SECTIONS ---"
        )
        profile_block = (
            f"--- BEGIN PDF EXTRACTED PROFILE ---\n"
            f"{profile_text}\n"
            f"--- END PDF EXTRACTED PROFILE ---"
        )
        prompt = f"""
SYSTEM: You are a professional career coach and LinkedIn optimization expert.

Your task is to:
1. Analyze the user’s provided job description or target role.
   - If both a role and company are provided (e.g., “AIML Engineer at Google”), infer the company's values, culture, and expectations.
   - If only a role is provided (e.g., “Junior Data Analyst”), do not assume any specific company. Build content that is compelling for service-based, product-based, and startup companies.
2. Evaluate the user’s current LinkedIn profile for alignment with the target.
3. Identify what aligns well and what falls short.
4. Provide actionable improvement suggestions.
5. Rebuild the LinkedIn profile from scratch to achieve a perfect **100/100 score**, using strict markdown formatting, recruiter-friendly tone, and realistic, non-fictional content.

---

INPUT CONTEXT:  
Job Description or Target Role:  
{jd_text}  

User LinkedIn Profile:  
{profile_block}{extra_block}

---

STRICT INSTRUCTIONS:

1. Output **exactly 17 sections**, in the following order:
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
   17. Any Other Relevant Section

2. For **each section**, include:
   - **Bold heading**: `### Section Name`
   - **Bold subheaders**: `**Weaknesses:**`, `**Suggestions:**`, and `**Rewritten Example:**`
   - Provide realistic critique or content in each

3. Never skip, merge, rename, or reorder any section. All 17 sections must be present—even if the user left them blank.

4. If any section is unclear or missing:
   - Create a **realistic placeholder** (e.g., GitHub repo, blog post, certification, recommendation prompt).
   - Never invent jobs or experiences not in the user's input.

5. Use the PDF and any extra user-provided sections as factual ground truth. You may rewrite wording for clarity, tone, and impact, but do not fabricate roles, employers, dates, credentials, teams, or numeric metrics. If the source lacks metrics, use non-numeric proof points (scope, technologies, responsibilities) without inventing numbers. Do not omit materially important information from the source.

6. Follow strict **Markdown-only** formatting:
   - No HTML or tables
   - No emojis
   - No decorative symbols
   - Use clean, professional formatting for every section

7. Your writing must sound **natural and recruiter-friendly**, never robotic, bloated, or overly templated.
8. Do not include the internal checklist in your output.
9. For the **Profile Summary (About)** section, open with a sharp, concise value hook that clearly states the candidate’s role focus, credible differentiators, and a concrete strength or metric (only if present in the source). Follow with 2–3 concrete proof points (scope, technologies, domains, or outcomes). Avoid clichés and filler (e.g., "passionate", "results-oriented", "hardworking"). Optionally close with a subtle call-to-action aligned to the target role/company.
10. Make the About section memorable by including a brief micro-story or one-sentence case study (from the source) that names specific technologies, datasets, domains, or stakeholders and the outcome achieved.
11. Prefer concrete nouns and proper nouns (tools, frameworks, clouds, datasets, industries) over generic adjectives. Avoid buzzword chains.
12. Keep sentences tight and varied; ensure the first sentence can stand alone as a distinctive value hook.
13. Profile Summary (About) rules:
    - First sentence must be a distinctive value hook that could stand alone in a recruiter search result.
    - Include 2–3 proof points with technologies, domains, and real outcomes from the source.
    - Optionally close with a subtle call-to-action aligned to the target role/company.
    - Include a brief micro-story or case study from the source — a single sentence naming stakeholders, tools, and the impact.
    - Keep it concise, varied in sentence length, and optimized for LinkedIn’s 2-line preview.
14. After the Current Profile Score, include a short "Verdict" section that summarizes practical recruiter value and what would be needed to reach a practical 100 using the provided template in the Output Format.
15. Volunteering: If the source does not mention volunteering, provide a realistic placeholder tied to college or community events (e.g., event coordination, hackathon volunteering, campus outreach). Do not use brand-name nonprofits unless present in the source. Keep the scope credible and aligned to the user’s domain where possible.
16. Languages: Only include spoken languages. If proficiency levels are present in the source, annotate each language with a concise level in parentheses using Title Case (acceptable set: Native, Fluent, Professional, Intermediate, Conversational). Do not infer or fabricate proficiency levels. If no level is provided, list the language without a level.
17. Headline: Lead with the role focus and specialization, add 2–3 high-value keywords (tools, domains), and avoid fluff.
18. Experience bullets: Use action-first, outcome-oriented bullets (STAR-aligned). Prefer metrics from the source; if no numbers exist, use scope/complexity/quality proof points. Keep 2–5 bullets per role.
19. Skills: Group into clear categories (e.g., Programming Languages, Frameworks/Libraries, Data/ML, Cloud/DevOps, Tools & Platforms, Soft/Analytical Skills). Remove duplicates, prefer canonical names, and cap each category to the most relevant ~8 items.
20. Projects: For each project, provide a one-line hook (problem + outcome), 1–2 bullets with technologies and impact, and a GitHub link (if present in source).
21. Recommendations: If real recommendations are absent, include 2 short, role-specific recommendation request prompts tailored to past collaborators or managers.

---

### SCORING TO ACHIEVE 100/100:

    - If a company is mentioned, it must appear in: Summary, Headline, and Experience
    - If no company is mentioned, the profile must be general but suitable for service, product, and startup contexts
    - Include business impact, teamwork, collaboration, and quantifiable results in Experience and Projects
    - About section: strong differentiating hook, 2–3 proof points with technologies/domains/outcomes, aligned to the target role; includes a subtle CTA; avoids clichés and filler
    - About section includes a concise micro-story or one-sentence case study with proper nouns from the source (e.g., tools, datasets, domains, stakeholders)
    - Uses concrete nouns/proper nouns and avoids generic adjectives or buzzword chains; first sentence can stand alone as a memorable value hook
    - Optimized for LinkedIn’s 2-line preview (role focus and differentiators surfaced immediately)
    - Distinctiveness: highlights unique differentiators compared to typical profiles
    - Volunteering: present and realistic; if absent in the source, uses a credible college/community event placeholder aligned to the domain
    - Languages: only spoken languages included; proficiency levels shown only when present in the source (Native/Fluent/Professional/Intermediate), otherwise omitted; no guessing
    - Include at least two projects (real or placeholder) with GitHub links and impact metrics
    - Mention MLflow, Weights & Biases, or reproducibility tools if relevant
    - Include ethical or responsible AI practices if applicable to the role
    - Include at least one professional certification
    - Include a realistic publication if none exists
    - Only list spoken languages in "Languages"
    - Include relevant Volunteering (e.g., college events) and Organizations participation if applicable
    - Personal Interests should show personality and/or alignment with the domain
    - Ensure the Skills section avoids duplicate or redundant entries (e.g., repeating "ASP.NET" and "ASP.NET Core"). Group related technologies where appropriate and remove overlaps.
    - Headline adheres to surfaces role focus + 2–3 high-value keywords
    - Experience bullets are action/outcome oriented; metrics when present, scope/quality when not
    - Skills are grouped, deduplicated, and focused on the most relevant items
    - Projects include hooks, technologies, impact, and GitHub links when present
    - Recommendations include at least two ready-to-send prompts if real ones are missing
    - "Any Other Relevant Section" includes GitHub and portfolio links when present in the source (otherwise include a clear action item to add them)

---

### OUTPUT FORMAT

**Target Role:** <role>  
**Target Company:** <company or "General / All Companies">

---

## Current Profile Score  
**Score:** <0–100>  
**Rationale:** <Short summary of alignment gaps and highlights>

---

## Verdict
Your profile is currently delivering something in the <90–95> range in practical recruiter value, which is very good for most LinkedIn profiles.
But a true practical 100 would require:
- High-impact hooks in About.
- Consistent business context & results in every experience.
- Better skills structuring.
- Multiple strong, real recommendations.
- More proof via links or media.

Minor gaps they’d see:
- Skills list could be structured for faster scanning (Technical Skills vs Soft/Analytical Skills).
- Personal Interests could connect more to role and some personal for brand alignment.

---

## Section-by-Section Audit

### Profile Summary (About)  
**Weaknesses:**  
…  
**Suggestions:**  
…  
**Rewritten Example:**  
…

*(Repeat this for all 17 sections, in order, using markdown formatting)*

---

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

### Any Other Relevant Section  
<Rewritten Example from section 17>

---

## Final Profile Score  
**Score:** <0–100>  
**Remarks:** <One-line summary>  
**Name:** <Full Name from input>

---

### FINAL AI CHECKLIST (Internal Only – Don't Output)

- [ ] All 17 sections present and in exact order  
- [ ] Each has Weaknesses, Suggestions, and Rewritten Example  
- [ ] Only real languages in “Languages”  
- [ ] “Personal Interests” meaningfully filled  
- [ ] If company is specified: mentioned in Summary, Headline 
- [ ] If no company: profile is general but strong  
- [ ] At least one certification included  
- [ ] Reproducibility, ethical AI, or open-source included if applicable  
- [ ] GitHub and portfolio in final section  
- [ ] Follows strict markdown format
- [ ] Includes a Verdict section after Current Profile Score


"""
        print("\n\n==== USER-PASTED EXTRA BLOCK ====")
        print(extra_block)
        print("==== END EXTRA BLOCK ====")
     
        return prompt


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

    prompt = build_prompt(profile_text, jd_text, extra_sections)

    def send_prompt_with_retries(prompt_text: str, max_api_retries: int = 4):
        """Send the prompt to Gemini with retry logic for transient errors (429/5xx).

        - Tries a small set of fallback models/endpoints on each attempt.
        - Exponential backoff with jitter between attempts.
        - Returns response JSON on success; raises the last exception otherwise.
        """
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
        candidate_endpoints = [
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        ]
        last_error = None
        for attempt_index in range(max_api_retries):
            for ep in candidate_endpoints:
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
                    return response.json()
                except (requests.Timeout, requests.ConnectionError) as e:
                    last_error = e
                    continue

            # Backoff before the next attempt across endpoints
            sleep_seconds = min(2 ** attempt_index + random.uniform(0, 0.5), 10)
            try:
                time.sleep(sleep_seconds)
            except Exception:
                pass

        # If all attempts exhausted
        if last_error:
            raise last_error
        raise Exception("Failed to get response after retries.")
    tries = 0
    max_tries = 2
    last_response = None

    while tries < max_tries:
        try:
            data = send_prompt_with_retries(prompt)

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

        except (requests.Timeout, requests.ConnectionError) as _net_err:
            tries += 1
            continue  # Retry on network issues
        except requests.HTTPError as http_err:
            # Transient 5xx/429 would have been retried above; return friendly error
            return (
                "Error: Service temporarily unavailable from Gemini API. "
                "Please try again shortly. Details: " + str(http_err)
            )

        except Exception as e:
            return f"Error: {str(e)}"

    # Return the last response if all retries fail (even if incomplete)
    return last_response or "Error: Gemini API did not return a usable response."
