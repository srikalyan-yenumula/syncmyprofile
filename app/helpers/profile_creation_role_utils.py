from .company_prompts import get_company_prompt
from .genai_utils import call_gemini_with_retries
from .logging_utils import get_logger, log_analysis_details, safe_log_text
from .role_prompts import get_role_prompt

logger = get_logger(__name__)


def create_linkedin_profile(user_data):
    """
    Generates a LinkedIn profile based on structured user input.
    user_data is a dictionary containing fields like name, education, skills, etc.
    """

    job_role = user_data.get("job_role", "General Professional")
    company_name = user_data.get("company_name", "")

    profile_input_block = "--- BEGIN USER INPUT DATA ---\n"
    for key, value in user_data.items():
        if key not in ["job_role", "company_name"]:
            profile_input_block += f"**{key.replace('_', ' ').title()}:**\n{value}\n\n"
    profile_input_block += "--- END USER INPUT DATA ---"

    role_prompt_content = get_role_prompt(job_role)
    logger.info(
        "Role prompt preview for profile creation=%s",
        safe_log_text(role_prompt_content, max_length=160),
    )

    if company_name:
        company_prompt_content = get_company_prompt(company_name)
        logger.info(
            "Company prompt preview for profile creation=%s",
            safe_log_text(company_prompt_content, max_length=160),
        )
    else:
        company_prompt_content = "No specific company provided. Focus on general industry standards."

    prompt = f"""
<system_instructions>
You are an expert Career Coach, ATS Specialist, and LinkedIn Profile Optimizer.
Your goal is to create a top-tier, 100/100 scored LinkedIn profile from scratch based on provided user data, perfectly aligned with a specific target role and company culture.
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
    {profile_input_block}
</user_data>

<task_description>
1.  **Analyze**: Deeply analyze the user's provided input data against the Target Role and Company Guidelines. Identify key strengths to highlight.
2.  **Strategize**: Determine the best angle to position this candidate. How can their provided background be framed to look perfect for this specific role?
3.  **Create**: Draft the profile sections to achieve a **100/100 score**.
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
    *   **Missing Info**: If a section is missing in the user input, you MUST create a **realistic placeholder** or suggestion based on the target role. Do not leave it empty.
    *   **Content Duplication**: You MUST generate the full content in the 'Section-by-Section Audit' (under 'Rewritten Example') **FIRST**. Then, copy it to the 'Rebuilt Profile' section.
4.  **Tone & Style (Human & Direct)**:
    *   **Simple & Real**: Write like a busy, high-performing human. Avoid "AI-polished" elegance. Be direct and punchy.
    *   **Recruiter-Ready**: Optimized for a 6-second scan. No walls of text.
    *   **Active Voice**: Start with strong verbs (e.g., "Led," "Built," "Saved").
5.  **Prohibition**: Do NOT explicitly mention the target company name in the created content unless it was in the user's input. Match their *style*, don't name-drop them.
</output_requirements>

<output_format>
**Target Role:** {job_role}
**Target Company:** {company_name if company_name else "General / All Companies"}

---

## Current Profile Score
**Score:** [0-100]
**Rationale:** [Assessment of the raw input quality]

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

### FINAL AI CHECKLIST (Internal Only â€“ Don't Output)
- [ ] All 17 sections present
- [ ] Markdown format strict
- [ ] No company name-dropping
</output_format>
"""

    response = call_gemini_with_retries(prompt)

    log_data = {
        "type": "profile_creation",
        "inputs": user_data,
        "prompts": {
            "role_prompt": role_prompt_content,
            "company_prompt": company_prompt_content,
        },
        "final_prompt": prompt,
        "output": response,
    }
    log_analysis_details(log_data)

    return response
