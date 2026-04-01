import os
import re
import shutil
from typing import Optional

from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from .helpers.pdf_utils import extract_text_from_pdf
from .helpers.job_role_utils import analyze_job_role
from .helpers.job_description_utils import analyze_job_description
from .helpers.resume_role_utils import analyze_resume_role
from .helpers.resume_job_description_utils import analyze_resume_job_description
from .helpers.profile_creation_role_utils import create_linkedin_profile
from .helpers.profile_creation_jd_utils import create_linkedin_profile_from_jd
from .helpers.logging_utils import configure_runtime_logging, get_logger, safe_log_text
from .helpers.session_utils import session_store

# Load environment variables
load_dotenv()
configure_runtime_logging()

logger = get_logger(__name__)

app = FastAPI()

if not os.getenv("GEMINI_API_KEY"):
    logger.warning(
        "GEMINI_API_KEY is not set. The server can start, but AI generation routes will return a readable error until configured."
    )

# Configuration
UPLOAD_FOLDER = 'data/uploads/'
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Custom filter for bold formatting
from markupsafe import Markup

def format_bold(text):
    # Replace **text** with <b>text</b>
    # Handle **Key:** Value
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return Markup(formatted)

templates.env.filters['format_bold'] = format_bold

# Helper to check allowed file extensions
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dependency to get or create session ID
async def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = session_store.create_session()
    return session_id

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = session_store.create_session()
        response = await call_next(request)
        response.set_cookie(key="session_id", value=session_id)
        return response
    else:
        response = await call_next(request)
        return response

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/landing", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/start", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/resume-start", response_class=HTMLResponse)
async def resume_start(request: Request):
    return templates.TemplateResponse("resume_upload.html", {"request": request})

@app.get("/select-service", response_class=HTMLResponse)
async def select_service(request: Request):
    return templates.TemplateResponse("options.html", {"request": request})

@app.post("/analyze")
async def analyze(
    request: Request,
    profile_pdf: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    job_desc: Optional[str] = Form(None),
    extra_sections: Optional[str] = Form(""),
    upload_type: str = Form("linkedin")
):
    session_id = request.cookies.get("session_id")
    if not session_id:
        # Should be handled by middleware, but safety check
        return JSONResponse({"error": "Session not initialized"}, status_code=400)

    logger.info(
        "Received analyze request with upload_type=%s and extra_sections_length=%s",
        safe_log_text(upload_type),
        len(extra_sections or ""),
    )

    if not profile_pdf or not allowed_file(profile_pdf.filename):
        return JSONResponse({"error": "A valid LinkedIn profile PDF is required."}, status_code=400)

    filename = secure_filename(profile_pdf.filename)
    profile_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(profile_path, "wb") as buffer:
        shutil.copyfileobj(profile_pdf.file, buffer)

    profile_text = extract_text_from_pdf(profile_path)
    logger.info("PDF text extraction completed for analyze request")

    analysis = None

    if job_desc and job_desc.strip():
        logger.info("Running job description analysis")
        if upload_type == 'resume':
            analysis = analyze_resume_job_description(profile_text, job_desc.strip(), extra_sections)
        else:
            analysis = analyze_job_description(profile_text, job_desc.strip(), extra_sections)
    elif job_role and job_role.strip():
        logger.info("Running job role analysis")
        if upload_type == 'resume':
            analysis = analyze_resume_role(profile_text, job_role.strip(), company_name.strip() if company_name else None, extra_sections)
        else:
            analysis = analyze_job_role(profile_text, job_role.strip(), company_name.strip() if company_name else None, extra_sections)
    else:
        return JSONResponse({"error": "Please provide either a job description or a target role."}, status_code=400)

    logger.info("Analyze request completed AI call")

    session_data = session_store.get_session(session_id)

    if analysis is None or (isinstance(analysis, str) and analysis.startswith('Error')):
        session_data["suggestion"] = None
        session_data["error"] = (
            "The AI service is temporarily unavailable. Please try again in a minute."
            if (isinstance(analysis, str) and 'temporarily unavailable' in analysis)
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
    
    suggestion_text = session_data.get('suggestion')
    error = session_data.get('error')

    if error:
        return templates.TemplateResponse("result.html", {"request": request, "error": error})
    
    if suggestion_text:
        try:
            parsed = parse_ai_markdown(suggestion_text)
            logger.info("Suggestion GET parsed and rendered successfully")
            
            if not parsed or not parsed.get('sections'):
                 return templates.TemplateResponse("result.html", {"request": request, "error": 'Parsing failed or no sections found.', "raw_output": suggestion_text})

            # Ensure rebuilt_profile is always defined
            if 'rebuilt_profile' not in parsed or parsed['rebuilt_profile'] is None:
                parsed['rebuilt_profile'] = {
                    'summary': '', 'experience': [], 'projects': [], 'skills': [],
                    'education': [], 'certifications': [], 'awards': [],
                    'languages': [], 'personal interests': [],
                }
            
            context = {"request": request, **parsed}
            return templates.TemplateResponse("result.html", context)
        except Exception as e:
            logger.exception("Error parsing AI response during suggestion GET")
            return templates.TemplateResponse("result.html", {"request": request, "error": f'Error parsing AI response: {str(e)}', "raw_output": suggestion_text})

    # Fallback empty
    return templates.TemplateResponse("result.html", {
        "request": request,
        "current_score": 0,
        "previous_score": 0,
        "improvement": 0,
        "target_role": '',
        "sections": [],
        "rebuilt_profile": {
            'summary': '', 'experience': [], 'projects': [], 'skills': [],
            'education': [], 'certifications': [], 'awards': [],
            'languages': [], 'personal interests': [],
        }
    })

@app.post("/suggestion", response_class=HTMLResponse)
async def suggestion_post(
    request: Request,
    profile_pdf: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    job_desc: Optional[str] = Form(None),
    extra_sections: Optional[str] = Form(""),
    upload_type: str = Form("linkedin")
):
    # Logic similar to analyze but renders template directly
    if not profile_pdf or not allowed_file(profile_pdf.filename):
         return templates.TemplateResponse("result.html", {"request": request, "error": "A valid LinkedIn profile PDF is required."})
    
    if (not job_desc or not job_desc.strip()) and (not job_role or not job_role.strip()):
        return templates.TemplateResponse("result.html", {"request": request, "error": "Please provide at least a job description or a target job role/title."})

    filename = secure_filename(profile_pdf.filename)
    profile_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(profile_path, "wb") as buffer:
        shutil.copyfileobj(profile_pdf.file, buffer)
        
    profile_text = extract_text_from_pdf(profile_path)
    logger.info("PDF text extraction completed for suggestion POST")



    if profile_text.startswith('Error'):
         return templates.TemplateResponse("result.html", {"request": request, "error": profile_text})

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
        analysis = analyze_job_role(profile_text, job_role.strip(), company_name.strip() if company_name else None, extra_sections)
    
    logger.info("Suggestion POST completed AI call")

    if analysis is None or (isinstance(analysis, str) and analysis.startswith('Error')):
        friendly = (
            'The AI service is temporarily unavailable. Please try again in a minute.'
            if (isinstance(analysis, str) and 'temporarily unavailable' in analysis)
            else analysis or 'Unknown error during analysis.'
        )
        return templates.TemplateResponse("result.html", {"request": request, "error": friendly})

    try:
        parsed = parse_ai_markdown(analysis)
        logger.info("Suggestion POST parsed and rendered successfully")
        
        if not parsed or not parsed.get('sections'):
             return templates.TemplateResponse("result.html", {"request": request, "error": 'Parsing failed or no sections found.', "raw_output": analysis})

        if 'rebuilt_profile' not in parsed or parsed['rebuilt_profile'] is None:
                parsed['rebuilt_profile'] = {
                    'summary': '', 'experience': [], 'projects': [], 'skills': [],
                    'education': [], 'certifications': [], 'awards': [],
                    'languages': [], 'personal interests': [],
                }

        return templates.TemplateResponse("result.html", {"request": request, **parsed})
    except Exception as e:
        logger.exception("Error parsing AI response during suggestion POST")
        return templates.TemplateResponse("result.html", {"request": request, "error": f'Error parsing AI response: {str(e)}', "raw_output": analysis})


@app.get("/create-profile", response_class=HTMLResponse)
async def create_profile(request: Request):
    return templates.TemplateResponse("create_profile.html", {"request": request})

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
    target_mode: Optional[str] = Form(None)
):
    user_data = {
        'full_name': full_name,
        'education': education,
        'skills': skills,
        'certifications': certifications,
        'courses': courses,
        'projects': projects,
        'awards': awards,
        'experience': experience,
        'volunteering': volunteering,
        'organizations': organizations,
        'languages': languages,
        'publications': publications,
        'licenses': licenses,
        'extra_info': extra_info,
        'job_role': job_role,
        'company_name': company_name
    }
    
    # Clean up None values
    user_data = {k: v for k, v in user_data.items() if v is not None and v.strip() != ''}
    
    logger.info(
        "Generating profile with target_mode=%s and populated_fields=%s",
        safe_log_text(target_mode or "role"),
        len(user_data),
    )
    
    if target_mode == 'jd' and job_description and job_description.strip():
        logger.info("Using job description mode for profile generation")
        analysis = create_linkedin_profile_from_jd(user_data, job_description)
    else:
        logger.info("Using role/company mode for profile generation")
        analysis = create_linkedin_profile(user_data)
    
    if analysis is None or (isinstance(analysis, str) and analysis.startswith('Error')):
        return templates.TemplateResponse("result.html", {"request": request, "error": analysis or "Unknown error during generation."})

    try:
        parsed = parse_ai_markdown(analysis)
        if not parsed or not parsed.get('sections'):
             return templates.TemplateResponse("result.html", {"request": request, "error": 'Parsing failed or no sections found.', "raw_output": analysis})
             
        return templates.TemplateResponse("result.html", {"request": request, **parsed})
    except Exception as e:
        logger.exception("Error parsing AI response during profile generation")
        return templates.TemplateResponse("result.html", {"request": request, "error": f'Error parsing AI response: {str(e)}', "raw_output": analysis})


# --- COPY OF parse_ai_markdown from app.py (adapted if needed) ---
def parse_ai_markdown(suggestion):
    # Strip AI control markers and separators from the raw suggestion first
    s = suggestion or ""
    # Remove block markers like <<<REBUILT_PROFILE_START>>> etc.
    s = re.sub(r"<<<[^>\n]+>>>", "", s)
    # Remove horizontal rules consisting of only --- on a line
    s = re.sub(r"^\s*---\s*$", "", s, flags=re.MULTILINE)
    # Remove lines that became only commas/whitespace after marker removal
    s = re.sub(r"^[\s,]+$", "", s, flags=re.MULTILINE)
    # Collapse excessive blank lines
    s = re.sub(r"\n{3,}", "\n\n", s)

    # Extract Name from the response
    name_match = re.search(r'\*\*Name:\*\*\s*(.+?)(?:\n|$)', s, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "Name not found"
    logger.debug("Parsed AI markdown name=%s", safe_log_text(name))

    # Extract Education from the response
    education_match = re.search(r'### Education\s*(.*?)(?=###|$)', s, re.DOTALL)
    education = education_match.group(1).strip() if education_match else "Education not found"
    logger.debug(
        "Parsed AI markdown education section preview=%s",
        safe_log_text(education, max_length=120),
    )

    # Extract Target Role from the very top if present
    top_role_match = re.search(r'^\*\*Target Role:\*\*\s*(.+)$', s, re.MULTILINE)
    if top_role_match:
        target_role = top_role_match.group(1).strip()
    else:
        # Fallback: Extract Target Role (if present) from previous logic
        target_role_match = re.search(r'Target (Job )?Role/Title:\s*(.*)', s)
        target_role = target_role_match.group(2).strip() if target_role_match else ""
    logger.debug("Parsed AI markdown target_role=%s", safe_log_text(target_role))

    # Extract Current Profile Score (before improvements) from API response
    score_match = re.search(r'##\s*Current Profile Score.*?\*\*Score:\*\*\s*(\d+)', s, re.DOTALL)
    previous_score = int(score_match.group(1)) if score_match else 0

    # Extract New Score After Improvements (final profile score) from API response
    final_score_match = re.search(r'##\s*[⭐️\*]*\s*Final Profile Score.*?\*\*Score:\*\*\s*(\d+)', s, re.DOTALL)
    current_score = int(final_score_match.group(1)) if final_score_match else previous_score

    # Extract rationale from the Current Profile Score section
    rationale_match = re.search(r'##\s*Current Profile Score.*?Rationale:\s*(.*?)(?:\n\s*[-*]|\n\s*Score:|\n\s*$)', s, re.DOTALL)
    rationale = rationale_match.group(1).strip() if rationale_match else ""

    # Clean the rationale to remove any headings like '## Section-by-Section Audit' or '### Profile Summary (About)'
    if rationale:
        rationale = re.split(r'\n+## |\n+### ', rationale)[0].strip()
        rationale = rationale.replace('**', '')

    # Calculate improvement
    improvement = current_score - previous_score

    # --- Robust Section-by-Section Parsing ---
    # 1. Extract the Section-by-Section Audit block
    # Allow ## or ###, case insensitive, allow extra spaces
    section_audit = re.search(r'#{2,3}\s*Section-by-Section Audit(.*?)(?:#{2,3}\s*Rebuilt Profile|$)', s, re.DOTALL | re.IGNORECASE)
    section_text = section_audit.group(1) if section_audit else ""
    if not section_text:
        # Fallback: try to find just the start if end marker is missing
        section_audit = re.search(r'#{2,3}\s*Section-by-Section Audit(.*)', s, re.DOTALL | re.IGNORECASE)
        section_text = section_audit.group(1) if section_audit else ""

    # 2. Split into sections by heading
    section_blocks = re.split(r'\n###\s*', section_text)
    sections = []
    for block in section_blocks:
        block = block.strip()
        if not block:
            continue
        # The first line is the section title
        lines = block.splitlines()
        title = lines[0].strip() if lines else "Untitled Section"
        rest = "\n".join(lines[1:])

        # Extract fields with tolerant regex (allow blank lines, extra spaces, any order)
        # Extract fields with tolerant regex (allow blank lines, extra spaces, any order)
        def extract_field(label, text):
            # Match **Label:** or **Label** or **Label**: etc.
            # Capture until the next real field label or section boundary
            boundary_labels = r"Weaknesses|Suggestions|Rewritten\s+Example"
            # Pattern explanation:
            # \*\*              Match opening bold
            # {label}           Match the label text
            # (?::)?            Match optional colon inside bold
            # \*\*              Match closing bold
            # (?::)?            Match optional colon outside bold
            # \s*               Match whitespace
            # (.*?)             Capture content non-greedily
            # (?=...)           Lookahead for next field or section end
            pattern = rf"\*\*{label}(?::)?\*\*(?::)?\s*(.*?)(?=\n\*\*(?:{boundary_labels})(?::)?\*\*(?::)?|\n###|\Z)"
            m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else "No information provided."

        weaknesses = extract_field("Weaknesses", rest)
        suggestions = extract_field("Suggestions", rest)
        rewritten = extract_field("Rewritten Example", rest)

        # Split weaknesses/suggestions into lists
        weaknesses_list = [w.strip('- ').strip() for w in weaknesses.split('\n') if w.strip()]
        suggestions_list = [s.strip('- ').strip() for s in suggestions.split('\n') if s.strip()]

        # Cleanups for rewritten content by section
        cleaned_rewritten = rewritten
        if cleaned_rewritten:
            # Skills: convert **Label:** to Label:
            if title.strip().lower() == 'skills':
                cleaned_rewritten = re.sub(r"\*\*\s*([^*]+?)\s*:\s*\*\*", r"\1:", cleaned_rewritten)
                cleaned_rewritten = re.sub(r"\*\*\s*([^*]+?)\s*\*\*\s*:\s*", r"\1:", cleaned_rewritten)
            # Experience: strip bold wrappers like **Company** / **Title**
            elif title.strip().lower() == 'experience':
                cleaned_rewritten = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned_rewritten)
            # Education: strip bold wrappers in institution/degree lines
            elif title.strip().lower() == 'education':
                cleaned_rewritten = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned_rewritten)
            # Projects: strip bold wrappers in project headings
            elif title.strip().lower() == 'projects':
                cleaned_rewritten = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned_rewritten)
            # Awards & Accomplishments: strip bold wrappers in award titles
            elif title.strip().lower() == 'awards & accomplishments':
                cleaned_rewritten = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned_rewritten)
            # Certifications: strip bold wrappers in certification titles
            elif title.strip().lower() == 'certifications':
                cleaned_rewritten = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned_rewritten)

        sections.append({
            'title': title,
            'weaknesses': weaknesses_list or ["No information provided."],
            'suggestions': suggestions_list or ["No information provided."],
            'rewritten': (cleaned_rewritten or "No rewritten example available.")
        })

    # If sections is empty, fill with all required sections as placeholders
    if not sections:
        required_sections = [
            'Profile Summary (About)', 'Headline', 'Experience', 'Skills', 'Education', 'Projects', 'Certifications',
            'Awards & Accomplishments', 'Courses', 'Publications', 'Licenses', 'Volunteering', 'Organizations',
            'Recommendations', 'Languages', 'personal Interests', 'Any other relevant section'
        ]
        for sec in required_sections:
            sections.append({
                'title': sec,
                'weaknesses': ['No information provided.'],
                'suggestions': ['No information provided.'],
                'rewritten': 'No rewritten example available.'
            })

    # After sections are parsed:
    required_sections = [
        'Profile Summary (About)', 'Headline', 'Experience', 'Skills', 'Education', 'Projects', 'Certifications',
        'Awards & Accomplishments', 'Courses', 'Publications', 'Licenses', 'Volunteering', 'Organizations',
        'Recommendations', 'Languages', 'personal Interests', 'Any other relevant section'
    ]
    # Build a dict for fast lookup
    section_dict = {s['title'].strip().lower(): s for s in sections}
    for sec in required_sections:
        key = sec.strip().lower()
        if key not in section_dict:
            sections.append({
                'title': sec,
                'weaknesses': ['No information provided.'],
                'suggestions': ['No information provided.'],
                'rewritten': 'No rewritten example available.'
            })
    # Optionally, sort sections to match required order
    def section_sort_key(s):
        try:
            return required_sections.index(s['title'])
        except ValueError:
            return 999
    sections = sorted(sections, key=section_sort_key)

    # Extract rebuilt profile (improved: cut at start of Final Profile Score section)
    # Try multiple patterns to handle variations in AI output
    rebuilt_patterns = [
        r'## Rebuilt Profile.*?### HERE IS YOUR NEW LINKEDIN PROFILE:(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)', 
        r'## Rebuilt Profile.*?### HERE IS YOUR NEW LINKEDIN PROFILE(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)',
        r'## Rebuilt Profile(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)',
        r'### HERE IS YOUR NEW LINKEDIN PROFILE:(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)',
        r'### HERE IS YOUR NEW LINKEDIN PROFILE(.*?)(?:##\s*[⭐️\*]*\s*Final Profile Score|New Score After Improvements|$)'
    ]
    
    rebuilt_text = ""
    for pattern in rebuilt_patterns:
        rebuilt_match = re.search(pattern, s, re.DOTALL)
        if rebuilt_match:
            rebuilt_text = rebuilt_match.group(1).strip()
            break
    
    # If no pattern matched, try to extract anything after "Rebuilt Profile" section
    if not rebuilt_text:
        rebuilt_match = re.search(r'## Rebuilt Profile(.*)', s, re.DOTALL)
        if rebuilt_match:
            rebuilt_text = rebuilt_match.group(1).strip()
            # Remove any trailing sections
            rebuilt_text = re.split(r'\n##\s*[⭐️\*]*\s*Final Profile Score', rebuilt_text)[0]
            rebuilt_text = re.split(r'\n##\s*New Score After Improvements', rebuilt_text)[0]

    # Use the full rebuilt profile text for the summary (so the preview shows all sections)
    summary = rebuilt_text

    # Ensure skills and other sections keep formatting where bold headings like **Programming Languages:** may appear
    rebuilt_profile = {
        'summary': summary,
        'experience': [],
        'projects': [],
        'skills': [],
        'education': [],
        'certifications': [],
        'awards': [],
        'languages': [],
        'personal interests': [],
    }

    # Extract remarks from the Final Profile Score section
    remarks_match = re.search(r'##\s*[⭐️\*]*\s*Final Profile Score.*?\*\*Remarks:\*\*\s*(.*?)(?:\n|$)', s, re.DOTALL)
    remarks = remarks_match.group(1).strip() if remarks_match else ""

    return {
        'current_score': current_score,
        'previous_score': previous_score,
        'improvement': improvement,
        'target_role': target_role,
        'sections': sections,
        'rebuilt_profile': rebuilt_profile,
        'rationale': rationale,
        'remarks': remarks,
        'name': name,
        'education': education
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
