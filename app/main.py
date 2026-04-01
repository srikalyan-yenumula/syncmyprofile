import os
import re
import shutil
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from werkzeug.utils import secure_filename

from .helpers.job_description_utils import analyze_job_description
from .helpers.job_role_utils import analyze_job_role
from .helpers.logging_utils import configure_runtime_logging, get_logger, safe_log_text
from .helpers.pdf_utils import extract_text_from_pdf
from .helpers.profile_creation_jd_utils import create_linkedin_profile_from_jd
from .helpers.profile_creation_role_utils import create_linkedin_profile
from .helpers.resume_job_description_utils import analyze_resume_job_description
from .helpers.resume_role_utils import analyze_resume_role
from .helpers.session_utils import session_store

load_dotenv()
configure_runtime_logging()

logger = get_logger(__name__)

app = FastAPI()

if not os.getenv("GEMINI_API_KEY"):
    logger.warning(
        "GEMINI_API_KEY is not set. The server can start, but AI routes will return a readable error until configured."
    )

UPLOAD_FOLDER = "data/uploads/"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def format_bold(text):
    formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    return Markup(formatted)


templates.env.filters["format_bold"] = format_bold


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def render_template(request: Request, template_name: str, context: Optional[dict] = None):
    template_context = {"request": request}
    if context:
        template_context.update(context)
    return templates.TemplateResponse(request, template_name, template_context)


def default_rebuilt_profile():
    return {
        "summary": "",
        "experience": [],
        "projects": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "awards": [],
        "languages": [],
        "personal interests": [],
    }


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = session_store.create_session()
        response = await call_next(request)
        response.set_cookie(key="session_id", value=session_id)
        return response
    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render_template(request, "landing.html")


@app.get("/landing", response_class=HTMLResponse)
async def landing(request: Request):
    return render_template(request, "landing.html")


@app.get("/start", response_class=HTMLResponse)
async def start(request: Request):
    return render_template(request, "index.html")


@app.get("/resume-start", response_class=HTMLResponse)
async def resume_start(request: Request):
    return render_template(request, "resume_upload.html")


@app.get("/select-service", response_class=HTMLResponse)
async def select_service(request: Request):
    return render_template(request, "options.html")


@app.post("/analyze")
async def analyze(
    request: Request,
    profile_pdf: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    job_desc: Optional[str] = Form(None),
    extra_sections: Optional[str] = Form(""),
    upload_type: str = Form("linkedin"),
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse({"error": "Session not initialized"}, status_code=400)

    logger.info(
        "Received analyze request with upload_type=%s and extra_sections_length=%s",
        safe_log_text(upload_type),
        len(extra_sections or ""),
    )

    if not profile_pdf or not allowed_file(profile_pdf.filename):
        return JSONResponse(
            {"error": "A valid LinkedIn profile PDF is required."}, status_code=400
        )

    filename = secure_filename(profile_pdf.filename)
    profile_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(profile_path, "wb") as buffer:
        shutil.copyfileobj(profile_pdf.file, buffer)

    profile_text = extract_text_from_pdf(profile_path)
    logger.info("PDF text extraction completed for analyze request")

    analysis = None
    if job_desc and job_desc.strip():
        logger.info("Running job description analysis")
        if upload_type == "resume":
            analysis = analyze_resume_job_description(
                profile_text, job_desc.strip(), extra_sections
            )
        else:
            analysis = analyze_job_description(profile_text, job_desc.strip(), extra_sections)
    elif job_role and job_role.strip():
        logger.info("Running job role analysis")
        if upload_type == "resume":
            analysis = analyze_resume_role(
                profile_text,
                job_role.strip(),
                company_name.strip() if company_name else None,
                extra_sections,
            )
        else:
            analysis = analyze_job_role(
                profile_text,
                job_role.strip(),
                company_name.strip() if company_name else None,
                extra_sections,
            )
    else:
        return JSONResponse(
            {"error": "Please provide either a job description or a target role."},
            status_code=400,
        )

    logger.info("Analyze request completed AI call")

    session_data = session_store.get_session(session_id)
    if analysis is None or (isinstance(analysis, str) and analysis.startswith("Error")):
        session_data["suggestion"] = None
        session_data["error"] = (
            "The AI service is temporarily unavailable. Please try again in a minute."
            if isinstance(analysis, str) and "temporarily unavailable" in analysis
            else analysis or "Unknown error during analysis."
        )
    else:
        session_data["suggestion"] = analysis
        session_data["error"] = None

    session_store.save_session(session_id, session_data)
    return JSONResponse({"redirect": "/suggestion"})


@app.get("/suggestion", response_class=HTMLResponse)
async def suggestion_get(request: Request):
    session_id = request.cookies.get("session_id")
    session_data = session_store.get_session(session_id) if session_id else {}

    suggestion_text = session_data.get("suggestion")
    error = session_data.get("error")

    if error:
        return render_template(request, "result.html", {"error": error})

    if suggestion_text:
        try:
            parsed = parse_ai_markdown(suggestion_text)
            logger.info("Suggestion GET parsed and rendered successfully")

            if not parsed or not parsed.get("sections"):
                return render_template(
                    request,
                    "result.html",
                    {
                        "error": "Parsing failed or no sections found.",
                        "raw_output": suggestion_text,
                    },
                )

            if not parsed.get("rebuilt_profile"):
                parsed["rebuilt_profile"] = default_rebuilt_profile()

            return render_template(request, "result.html", parsed)
        except Exception as e:
            logger.exception("Error parsing AI response during suggestion GET")
            return render_template(
                request,
                "result.html",
                {
                    "error": f"Error parsing AI response: {str(e)}",
                    "raw_output": suggestion_text,
                },
            )

    return render_template(
        request,
        "result.html",
        {
            "current_score": 0,
            "previous_score": 0,
            "improvement": 0,
            "target_role": "",
            "sections": [],
            "rebuilt_profile": default_rebuilt_profile(),
        },
    )


@app.post("/suggestion", response_class=HTMLResponse)
async def suggestion_post(
    request: Request,
    profile_pdf: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    job_desc: Optional[str] = Form(None),
    extra_sections: Optional[str] = Form(""),
    upload_type: str = Form("linkedin"),
):
    if not profile_pdf or not allowed_file(profile_pdf.filename):
        return render_template(
            request,
            "result.html",
            {"error": "A valid LinkedIn profile PDF is required."},
        )

    if (not job_desc or not job_desc.strip()) and (not job_role or not job_role.strip()):
        return render_template(
            request,
            "result.html",
            {
                "error": "Please provide at least a job description or a target job role/title."
            },
        )

    filename = secure_filename(profile_pdf.filename)
    profile_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(profile_path, "wb") as buffer:
        shutil.copyfileobj(profile_pdf.file, buffer)

    profile_text = extract_text_from_pdf(profile_path)
    logger.info("PDF text extraction completed for suggestion POST")

    if profile_text.startswith("Error"):
        return render_template(request, "result.html", {"error": profile_text})

    logger.info(
        "Received suggestion POST with upload_type=%s and extra_sections_length=%s",
        safe_log_text(upload_type),
        len(extra_sections or ""),
    )

    analysis = None
    if job_desc and job_desc.strip():
        logger.info("Running job description analysis for suggestion POST")
        analysis = analyze_job_description(profile_text, job_desc.strip(), extra_sections)
    elif job_role and job_role.strip():
        logger.info("Running job role analysis for suggestion POST")
        analysis = analyze_job_role(
            profile_text,
            job_role.strip(),
            company_name.strip() if company_name else None,
            extra_sections,
        )

    logger.info("Suggestion POST completed AI call")

    if analysis is None or (isinstance(analysis, str) and analysis.startswith("Error")):
        friendly = (
            "The AI service is temporarily unavailable. Please try again in a minute."
            if isinstance(analysis, str) and "temporarily unavailable" in analysis
            else analysis or "Unknown error during analysis."
        )
        return render_template(request, "result.html", {"error": friendly})

    try:
        parsed = parse_ai_markdown(analysis)
        logger.info("Suggestion POST parsed and rendered successfully")

        if not parsed or not parsed.get("sections"):
            return render_template(
                request,
                "result.html",
                {"error": "Parsing failed or no sections found.", "raw_output": analysis},
            )

        if not parsed.get("rebuilt_profile"):
            parsed["rebuilt_profile"] = default_rebuilt_profile()

        return render_template(request, "result.html", parsed)
    except Exception as e:
        logger.exception("Error parsing AI response during suggestion POST")
        return render_template(
            request,
            "result.html",
            {"error": f"Error parsing AI response: {str(e)}", "raw_output": analysis},
        )


@app.get("/create-profile", response_class=HTMLResponse)
async def create_profile_page(request: Request):
    return render_template(request, "create_profile.html")


@app.post("/generate-profile", response_class=HTMLResponse)
async def generate_profile(
    request: Request,
    full_name: str = Form(...),
    education: str = Form(...),
    skills: str = Form(...),
    certifications: Optional[str] = Form(None),
    courses: Optional[str] = Form(None),
    projects: Optional[str] = Form(None),
    awards: Optional[str] = Form(None),
    experience: Optional[str] = Form(None),
    volunteering: Optional[str] = Form(None),
    organizations: Optional[str] = Form(None),
    languages: Optional[str] = Form(None),
    publications: Optional[str] = Form(None),
    licenses: Optional[str] = Form(None),
    extra_info: Optional[str] = Form(None),
    job_role: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    target_mode: Optional[str] = Form(None),
):
    user_data = {
        "full_name": full_name,
        "education": education,
        "skills": skills,
        "certifications": certifications,
        "courses": courses,
        "projects": projects,
        "awards": awards,
        "experience": experience,
        "volunteering": volunteering,
        "organizations": organizations,
        "languages": languages,
        "publications": publications,
        "licenses": licenses,
        "extra_info": extra_info,
        "job_role": job_role,
        "company_name": company_name,
    }
    user_data = {k: v for k, v in user_data.items() if v is not None and v.strip() != ""}

    logger.info(
        "Generating profile with target_mode=%s and populated_fields=%s",
        safe_log_text(target_mode or "role"),
        len(user_data),
    )

    if target_mode == "jd" and job_description and job_description.strip():
        logger.info("Using job description mode for profile generation")
        analysis = create_linkedin_profile_from_jd(user_data, job_description)
    else:
        logger.info("Using role/company mode for profile generation")
        analysis = create_linkedin_profile(user_data)

    if analysis is None or (isinstance(analysis, str) and analysis.startswith("Error")):
        return render_template(
            request,
            "result.html",
            {"error": analysis or "Unknown error during generation."},
        )

    try:
        parsed = parse_ai_markdown(analysis)
        if not parsed or not parsed.get("sections"):
            return render_template(
                request,
                "result.html",
                {"error": "Parsing failed or no sections found.", "raw_output": analysis},
            )

        if not parsed.get("rebuilt_profile"):
            parsed["rebuilt_profile"] = default_rebuilt_profile()

        return render_template(request, "result.html", parsed)
    except Exception as e:
        logger.exception("Error parsing AI response during profile generation")
        return render_template(
            request,
            "result.html",
            {"error": f"Error parsing AI response: {str(e)}", "raw_output": analysis},
        )


def parse_ai_markdown(suggestion):
    s = suggestion or ""
    s = re.sub(r"<<<[^>\n]+>>>", "", s)
    s = re.sub(r"^\s*---\s*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"^[\s,]+$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\n{3,}", "\n\n", s)

    name_match = re.search(r"\*\*Name:\*\*\s*(.+?)(?:\n|$)", s, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "Name not found"
    logger.debug("Parsed AI markdown name=%s", safe_log_text(name))

    education_match = re.search(r"### Education\s*(.*?)(?=###|$)", s, re.DOTALL)
    education = education_match.group(1).strip() if education_match else "Education not found"
    logger.debug(
        "Parsed AI markdown education preview=%s",
        safe_log_text(education, max_length=120),
    )

    top_role_match = re.search(r"^\*\*Target Role:\*\*\s*(.+)$", s, re.MULTILINE)
    if top_role_match:
        target_role = top_role_match.group(1).strip()
    else:
        fallback_role_match = re.search(r"Target (Job )?Role/Title:\s*(.*)", s)
        target_role = fallback_role_match.group(2).strip() if fallback_role_match else ""
    logger.debug("Parsed AI markdown target_role=%s", safe_log_text(target_role))

    score_match = re.search(
        r"##\s*Current Profile Score.*?\*\*Score:\*\*\s*(\d+)", s, re.DOTALL
    )
    previous_score = int(score_match.group(1)) if score_match else 0

    final_score_match = re.search(
        r"##\s*[⭐️\*]*\s*Final Profile Score.*?\*\*Score:\*\*\s*(\d+)",
        s,
        re.DOTALL,
    )
    current_score = int(final_score_match.group(1)) if final_score_match else previous_score

    rationale_match = re.search(
        r"##\s*Current Profile Score.*?Rationale:\s*(.*?)(?:\n\s*[-*]|\n\s*Score:|\n\s*$)",
        s,
        re.DOTALL,
    )
    rationale = rationale_match.group(1).strip() if rationale_match else ""
    if rationale:
        rationale = re.split(r"\n+## |\n+### ", rationale)[0].strip()
        rationale = rationale.replace("**", "")

    improvement = current_score - previous_score

    section_audit = re.search(
        r"#{2,3}\s*Section-by-Section Audit(.*?)(?:#{2,3}\s*Rebuilt Profile|$)",
        s,
        re.DOTALL | re.IGNORECASE,
    )
    section_text = section_audit.group(1) if section_audit else ""
    if not section_text:
        fallback_audit = re.search(
            r"#{2,3}\s*Section-by-Section Audit(.*)", s, re.DOTALL | re.IGNORECASE
        )
        section_text = fallback_audit.group(1) if fallback_audit else ""

    section_blocks = re.split(r"\n###\s*", section_text)
    sections = []

    def extract_field(label, text):
        boundary_labels = r"Weaknesses|Suggestions|Rewritten\s+Example"
        pattern = rf"\*\*{label}(?::)?\*\*(?::)?\s*(.*?)(?=\n\*\*(?:{boundary_labels})(?::)?\*\*(?::)?|\n###|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else "No information provided."

    for block in section_blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        title = lines[0].strip() if lines else "Untitled Section"
        rest = "\n".join(lines[1:])
        weaknesses = extract_field("Weaknesses", rest)
        suggestions = extract_field("Suggestions", rest)
        rewritten = extract_field("Rewritten Example", rest)

        weaknesses_list = [w.strip("- ").strip() for w in weaknesses.split("\n") if w.strip()]
        suggestions_list = [s.strip("- ").strip() for s in suggestions.split("\n") if s.strip()]

        cleaned_rewritten = rewritten
        if cleaned_rewritten and title.strip().lower() in {
            "skills",
            "experience",
            "education",
            "projects",
            "awards & accomplishments",
            "certifications",
        }:
            cleaned_rewritten = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned_rewritten)
            if title.strip().lower() == "skills":
                cleaned_rewritten = re.sub(
                    r"\*\*\s*([^*]+?)\s*:\s*\*\*", r"\1:", cleaned_rewritten
                )
                cleaned_rewritten = re.sub(
                    r"\*\*\s*([^*]+?)\s*\*\*\s*:\s*", r"\1:", cleaned_rewritten
                )

        sections.append(
            {
                "title": title,
                "weaknesses": weaknesses_list or ["No information provided."],
                "suggestions": suggestions_list or ["No information provided."],
                "rewritten": cleaned_rewritten or "No rewritten example available.",
            }
        )

    if not sections:
        required_sections = [
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
            "personal Interests",
            "Any other relevant section",
        ]
        for sec in required_sections:
            sections.append(
                {
                    "title": sec,
                    "weaknesses": ["No information provided."],
                    "suggestions": ["No information provided."],
                    "rewritten": "No rewritten example available.",
                }
            )

    required_sections = [
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
        "personal Interests",
        "Any other relevant section",
    ]
    section_dict = {s["title"].strip().lower(): s for s in sections}
    for sec in required_sections:
        if sec.strip().lower() not in section_dict:
            sections.append(
                {
                    "title": sec,
                    "weaknesses": ["No information provided."],
                    "suggestions": ["No information provided."],
                    "rewritten": "No rewritten example available.",
                }
            )

    def section_sort_key(s):
        try:
            return required_sections.index(s["title"])
        except ValueError:
            return 999

    sections = sorted(sections, key=section_sort_key)

    rebuilt_patterns = [
        r"## Rebuilt Profile.*?### HERE IS YOUR NEW LINKEDIN PROFILE:(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)",
        r"## Rebuilt Profile.*?### HERE IS YOUR NEW LINKEDIN PROFILE(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)",
        r"## Rebuilt Profile(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)",
        r"### HERE IS YOUR NEW LINKEDIN PROFILE:(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)",
        r"### HERE IS YOUR NEW LINKEDIN PROFILE(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)",
    ]

    rebuilt_text = ""
    for pattern in rebuilt_patterns:
        rebuilt_match = re.search(pattern, s, re.DOTALL)
        if rebuilt_match:
            rebuilt_text = rebuilt_match.group(1).strip()
            break

    if not rebuilt_text:
        rebuilt_match = re.search(r"## Rebuilt Profile(.*)", s, re.DOTALL)
        if rebuilt_match:
            rebuilt_text = rebuilt_match.group(1).strip()
            rebuilt_text = re.split(r"\n##\s*[⭐️\*]*\s*Final Profile Score", rebuilt_text)[0]
            rebuilt_text = re.split(r"\n##\s*New Score After Improvements", rebuilt_text)[0]

    rebuilt_profile = {
        "summary": rebuilt_text,
        "experience": [],
        "projects": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "awards": [],
        "languages": [],
        "personal interests": [],
    }

    remarks_match = re.search(
        r"##\s*[⭐️\*]*\s*Final Profile Score.*?\*\*Remarks:\*\*\s*(.*?)(?:\n|$)",
        s,
        re.DOTALL,
    )
    remarks = remarks_match.group(1).strip() if remarks_match else ""

    return {
        "current_score": current_score,
        "previous_score": previous_score,
        "improvement": improvement,
        "target_role": target_role,
        "sections": sections,
        "rebuilt_profile": rebuilt_profile,
        "rationale": rationale,
        "remarks": remarks,
        "name": name,
        "education": education,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
