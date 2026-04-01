import json
import re
from .genai_utils import call_gemini_with_retries
from .company_prompts import get_company_prompt
from .role_prompts import get_role_prompt
from .logging_utils import get_logger, log_analysis_details, safe_log_text

logger = get_logger(__name__)

def extract_role_company_from_jd(jd_text):
    """
    Uses Gemini to extract the Job Role and Company Name from the JD text.
    Returns a tuple (role, company).
    """
    extraction_prompt = f"""
    Analyze the following Job Description and extract the 'Job Role' (Title) and 'Company Name'.
    
    Job Description:
    {jd_text[:2000]}  # Truncate to avoid huge context if JD is very long
    
    Return ONLY a JSON object with keys 'role' and 'company'.
    Example: {{"role": "Software Engineer", "company": "Google"}}
    If not found, return empty strings.
    """
    
    try:
        response = call_gemini_with_retries(extraction_prompt)
        # Clean up code blocks if present
        response = re.sub(r'```json', '', response)
        response = re.sub(r'```', '', response).strip()
        data = json.loads(response)
        return data.get('role', ''), data.get('company', '')
    except Exception as e:
        logger.warning("Error extracting role/company from JD: %s", safe_log_text(e))
        return '', ''

def create_linkedin_profile_from_jd(user_data, jd_text):
    """
    Generates a LinkedIn profile based on structured user input and a Job Description.
    user_data is a dictionary containing fields like name, education, skills, etc.
    jd_text is the raw text of the target Job Description.
    """
    
    # 1. Extract Role and Company from JD
    logger.info("Extracting role and company from JD")
    extracted_role, extracted_company = extract_role_company_from_jd(jd_text)
    logger.info("Extracted role=%s", safe_log_text(extracted_role))
    logger.info("Extracted company=%s", safe_log_text(extracted_company))

    # 2. Fetch specific prompts using extracted data
    role_prompt_content = ""
    if extracted_role:
        role_prompt_content = get_role_prompt(extracted_role)
        logger.info(
            "Role prompt preview for JD profile creation=%s",
            safe_log_text(role_prompt_content, max_length=160),
        )
    
    company_prompt_content = ""
    if extracted_company:
        company_prompt_content = get_company_prompt(extracted_company)
        logger.info(
            "Company prompt preview for JD profile creation=%s",
            safe_log_text(company_prompt_content, max_length=160),
        )

    # Construct a text representation of the user's input
    profile_input_block = "--- BEGIN USER INPUT DATA ---\n"
    for key, value in user_data.items():
        if key not in ['job_role', 'company_name']:
            profile_input_block += f"**{key.replace('_', ' ').title()}:**\n{value}\n\n"
    profile_input_block += "--- END USER INPUT DATA ---"

    prompt = f"""
<system_instructions>
You are an expert Career Coach, ATS Specialist, and LinkedIn Profile Optimizer.
Your goal is to create a top-tier, 100/100 scored LinkedIn profile from scratch based on provided user data, perfectly aligned with the provided Job Description (JD).
You must strictly follow the output format and structural requirements.
</system_instructions>

<context>
    <target_job_description>
    {jd_text}
    </target_job_description>
    
    <extracted_info>
    Target Role: {extracted_role}
    Target Company: {extracted_company}
    </extracted_info>
    
    <supplementary_guidelines>
    {role_prompt_content if role_prompt_content else "No specific role guidelines provided."}
    {company_prompt_content if company_prompt_content else "No specific company guidelines provided."}
    </supplementary_guidelines>
</context>

<user_data>
    {profile_input_block}
</user_data>

<task_description>
1.  **Analyze**: Deeply analyze the user's provided input data against the Target Job Description. Identify key keywords, skills, and requirements from the JD.
2.  **Strategize**: Determine the best angle to position this candidate. How can their provided background be framed to look perfect for this specific JD?
3.  **Create**: Draft the profile sections to achieve a **100/100 score**.
    *   **Score Criteria**:
        *   **JD Alignment (Critical)**: The profile MUST use the exact keywords and language found in the JD.
        *   About Section (20pts): Must have a killer hook, metric-driven proof points, and a micro-story.
        *   Experience (20pts): Action-oriented, STAR method, quantified results.
        *   Skills (15pts): Relevant, categorized, and keyword-rich (from JD).
        *   Projects (15pts): Depth, technical details, and outcomes.
        *   Certifications (10pts): Relevant to the role.
        *   Completeness (10pts): All 17 sections present.
        *   Alignment (10pts): Tone and keywords match the target company/role.
4.  **Output**: Generate the response in the strict format defined below.
</task_description>

<output_requirements>
1.  **Structure**: Output **exactly 17 sections** in the specific order listed below. Do not skip, merge, or reorder.
2.  **Format**: Use **Markdown** only. No HTML, no tables.
3.  **Content Constraints (STRICT)**:
    *   **About Section**: **MAX 3 short paragraphs**. Total reading time must be under 30 seconds. Focus on the "Value Hook" and 2-3 key proof points.
    *   **Experience**: **STRICT LIMIT: Max 3-4 bullet points per role.** Focus ONLY on high-impact results (ROI, growth, savings). Remove generic duties and technical fluff.
    *   **Projects**: **Select ONLY the top 2 most relevant projects.** Max 3 bullet points each. Do not overwhelm with technical details.
    *   **Skills**: **Select ONLY the top 12-15 most critical skills.** Do not list everything you know. Group them logically.
    *   **Missing Info**: If a section is missing in the user input, you MUST create a **realistic placeholder** or suggestion based on the target role. Do not leave it empty.
    *   **Content Duplication**: You MUST generate the full content in the 'Section-by-Section Audit' (under 'Rewritten Example') **FIRST**. Then, copy it to the 'Rebuilt Profile' section.
4.  **Tone & Style (Human & Direct)**:
    *   **Simple & Real**: Write like a busy, high-performing human. Avoid "AI-polished" elegance. Be direct and punchy.
    *   **Recruiter-Ready**: Optimized for a 6-second scan. No walls of text.
    *   **Active Voice**: Start with strong verbs (e.g., "Led," "Built," "Saved").
5.  **Prohibition**: Do NOT explicitly mention the target company name in the created content unless it was in the user's input. Match their *style*, don't name-drop them.
</output_requirements>

<output_format>
**Target Role:** {extracted_role if extracted_role else "[Extracted from JD]"}
**Target Company:** {extracted_company if extracted_company else "[Extracted from JD]"}

---

## Current Profile Score
**Score:** [0-100]
**Rationale:** [Assessment of the raw input quality vs JD]

---

## Verdict
[Short, punchy verdict on the potential of this profile based on inputs.]

---

## Section-by-Section Audit

### Headline
**Weaknesses:**
...
**Suggestions:**
...
**Rewritten Example:**
...

### Profile Summary (About)
**Weaknesses:**
...
**Suggestions:**
...
**Rewritten Example:**
...

[... Repeat for all 17 sections ...]

---

## Rebuilt Profile
### HERE IS YOUR NEW LINKEDIN PROFILE:

**Name:** {user_data.get('full_name', 'Your Name')}
**Headline:** [Optimized Headline]

### Profile Summary (About)
[Optimized Content]

### Experience
[Optimized Content]

### Skills
[Optimized Content]

### Education
[Optimized Content]

### Projects
[Optimized Content]

### Certifications
[Optimized Content]

### Awards & Accomplishments
[Optimized Content]

### Courses
[Optimized Content]

### Publications
[Optimized Content]

### Licenses
[Optimized Content]

### Volunteering
[Optimized Content]

### Organizations
[Optimized Content]

### Recommendations
[Optimized Content]

### Languages
[Optimized Content]

### Personal Interests
[Optimized Content]

### Any Other Relevant Section
[Optimized Content]

---

## Final Profile Score
**Score:** [0-100]
**Remarks:** [Final encouraging comment]
**Name:** {user_data.get('full_name', 'Your Name')}

---

### FINAL AI CHECKLIST (Internal Only – Don't Output)
- [ ] All 17 sections present
- [ ] Markdown format strict
- [ ] No company name-dropping
</output_format>
"""
    
    response = call_gemini_with_retries(prompt)

    # Log the analysis details
    log_data = {
        'type': 'profile_creation_jd',
        'inputs': user_data,
        'jd_length': len(jd_text),
        'prompts': {
            'role_prompt': role_prompt_content,
            'company_prompt': company_prompt_content
        },
        'final_prompt': prompt,
        'output': response
    }
    log_analysis_details(log_data)

    return response
