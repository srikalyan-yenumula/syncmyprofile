from .company_prompts import get_company_prompt
from .genai_utils import call_gemini_with_retries
from .logging_utils import get_logger, log_analysis_details, safe_log_text
from .role_prompts import get_role_prompt

logger = get_logger(__name__)


def analyze_job_role(profile_text, job_role, company_name=None, extra_sections=None):
    """
    Analyzes the profile specifically against a target Job Role and optional Company.
    """

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

    role_prompt_content = get_role_prompt(job_role)
    company_prompt_content = ""
    if company_name:
        company_prompt_content = get_company_prompt(company_name)
    else:
        company_prompt_content = "No specific company provided. Focus on general industry standards."

    logger.info(
        "Role prompt preview=%s",
        safe_log_text(role_prompt_content, max_length=100),
    )
    if company_name:
        logger.info(
            "Company prompt preview=%s",
            safe_log_text(company_prompt_content, max_length=100),
        )

    prompt = f"""
<system_instructions>
You are an expert Career Coach, ATS Specialist, and LinkedIn Profile Optimizer.
Your goal is to transform a user's LinkedIn profile into a top-tier, 100/100 scored profile that perfectly aligns with a specific target role and company culture.
You must strictly follow the output format and structural requirements.
</system_instructions>

<context>
    <target_role>{job_role}</target_role>
    <target_company>{company_name if company_name else 'General Industry Standards'}</target_company>
    <company_guidelines>
    {company_prompt_content}
    </company_guidelines>
    <role_guidelines>
    {role_prompt_content}
    </role_guidelines>
</context>

<user_data>
    <profile_content>
    {profile_block}
    </profile_content>
    <extra_sections>
    {extra_block}
    </extra_sections>
</user_data>

<task_description>
1.  **Analyze**: Deeply analyze the user's current profile against the Target Role and Company Guidelines. Identify gaps, weak language, and missing keywords.
2.  **Strategize**: Determine the best angle to position this candidate. How can their past experience be framed to look perfect for this specific role?
3.  **Rebuild**: Rewrite the profile sections to achieve a **100/100 score**.
    *   **Score Criteria**:
        *   About Section (20pts): Must have a killer hook, metric-driven proof points, and a micro-story.
        *   Experience (20pts): Action-oriented, STAR method, quantified results.
        *   Skills (15pts): Relevant, categorized, and keyword-rich.
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
    *   **Missing Info**: If a section is missing in the input, you MUST still generate a **Rewritten Example** for it (as a realistic placeholder or inferred content). Do not leave it empty.
    *   **Content Duplication**: You MUST generate the full rewritten content in the 'Section-by-Section Audit' (under 'Rewritten Example') **FIRST**. Then, copy it to the 'Rebuilt Profile' section. Never output "No rewritten example available" if you are able to generate one for the final profile.
4.  **Tone & Style (Human & Direct)**:
    *   **Simple & Real**: Write like a busy, high-performing human. Avoid "AI-polished" elegance. Be direct and punchy.
    *   **Recruiter-Ready**: Optimized for a 6-second scan. No walls of text.
    *   **Active Voice**: Start with strong verbs (e.g., "Led," "Built," "Saved").
5.  **Prohibition**: Do NOT explicitly mention the target company name in the rewritten content unless it was already in the source text. Match their *style*, don't name-drop them.
</output_requirements>

<output_format>
**Target Role:** {job_role}
**Target Company:** {company_name if company_name else "General / All Companies"}

---

## Current Profile Score
**Score:** [0-100]
**Rationale:** [Concise explanation of the score]

---

## Verdict
[Short, punchy verdict on the candidate's current standing vs. what is needed for a top-tier application.]

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

**Name:** [Extracted Name]
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
**Name:** [Extracted Name]

---

### FINAL AI CHECKLIST (Internal Only â€“ Don't Output)
- [ ] All 17 sections present
- [ ] Markdown format strict
- [ ] No company name-dropping
</output_format>
"""

    response = call_gemini_with_retries(prompt)

    log_data = {
        "type": "job_role_analysis",
        "inputs": {
            "profile_text": profile_text,
            "job_role": job_role,
            "company_name": company_name,
            "extra_sections": extra_sections,
        },
        "prompts": {
            "role_prompt": role_prompt_content,
            "company_prompt": company_prompt_content,
        },
        "final_prompt": prompt,
        "output": response,
    }
    log_analysis_details(log_data)

    return response
