import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.utils import secure_filename
from helpers.pdf_utils import extract_text_from_pdf
from helpers.genai_utils import analyze_profile
from dotenv import load_dotenv
import re
from flask_session import Session  # <-- Add this import


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_default_secret_key')
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'pdf'}

# Enable server-side session storage
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page with the upload form."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle AJAX analyze request, save PDF, run analysis, and redirect to suggestion page."""
    profile_file = request.files.get('profile_pdf')
    job_role = request.form.get('job_role')

    if not profile_file or not allowed_file(profile_file.filename):
        return jsonify({'error': 'A valid LinkedIn profile PDF is required.'}), 400

    filename = secure_filename(profile_file.filename)
    profile_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    profile_file.save(profile_path)
    profile_text = extract_text_from_pdf(profile_path)
    print('✅ PDF text extraction successful.')

    if profile_text.startswith('Error'):
        session['suggestion'] = None
        session['error'] = profile_text
        return jsonify({'redirect': url_for('suggestion')})

    jd_text = job_role
    analysis = analyze_profile(profile_text, jd_text)
    print('✅ Gemini API response received and stored in session.')
    
 
    if analysis is None or (isinstance(analysis, str) and analysis.startswith('Error')):
        session['suggestion'] = None
        session['error'] = analysis or 'Unknown error during analysis.'
        return jsonify({'redirect': url_for('suggestion')})
    # Store result in session and redirect
    session['suggestion'] = analysis
    session['error'] = None
    return jsonify({'redirect': url_for('suggestion')})

@app.route('/suggestion', methods=['GET', 'POST'])
def suggestion():
    """Render the result page with suggestions, handling both GET and POST."""
    if request.method == 'POST':
        profile_file = request.files.get('profile_pdf')
        job_desc = request.form.get('job_desc', '').strip()
        job_role = request.form.get('job_role', '').strip()

        if not profile_file or not allowed_file(profile_file.filename):
            return render_template('result.html', error="A valid LinkedIn profile PDF is required.")
        if not job_desc and not job_role:
            return render_template('result.html', error="Please provide at least a job description or a target job role/title.")

        filename = secure_filename(profile_file.filename)
        profile_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_file.save(profile_path)
        profile_text = extract_text_from_pdf(profile_path)
       
        print('✅ PDF text extraction successful.')
      

        if profile_text.startswith('Error'):
            return render_template('result.html', error=profile_text)

        # Compose the JD text for the AI prompt
        jd_text = ''
        if job_desc:
            jd_text += job_desc
        if job_role:
            if jd_text:
                jd_text += "\n\n"
            jd_text += f"Target Job Role/Title: {job_role}"

        analysis = analyze_profile(profile_text, jd_text)
     
        print('✅ Gemini API response received and stored in session.')
      
        if analysis is None or (isinstance(analysis, str) and analysis.startswith('Error')):
            return render_template('result.html', error=analysis or 'Unknown error during analysis.')
        parsed = parse_ai_markdown(analysis)
        print('✅ AI analysis parsed and ready to render.')
        
        if not parsed or not parsed.get('sections'):
            return render_template('result.html', error='Parsing failed or no sections found.', raw_output=analysis)
        return render_template('result.html', **parsed)
    else:
        # GET request: check for suggestion or error in session (use get, not pop)
        suggestion_text = session.get('suggestion', None)
        error = session.get('error', None)
        if error:
            return render_template('result.html', error=error)
        if suggestion_text:
            parsed = parse_ai_markdown(suggestion_text)
            print('✅ Suggestion (GET) parsed and displayed.')
            if not parsed or not parsed.get('sections'):
                return render_template('result.html', error='Parsing failed or no sections found.', raw_output=suggestion_text)
            return render_template('result.html', **parsed)
        # Fallback: Provide empty defaults for all template variables
        return render_template('result.html',
            current_score=0,
            previous_score=0,
            improvement=0,
            target_role='',
            sections=[],
            rebuilt_profile={
                'summary': '',
                'experience': [],
                'projects': [],
                'skills': [],
                'education': [],
                'certifications': [],
                'awards': [],
                'languages': [],
                'interests': [],
            }
        )

def parse_ai_markdown(suggestion):
    # Extract Name from the response
    name_match = re.search(r'\*\*Name:\*\*\s*(.+?)(?:\n|$)', suggestion, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else "Name not found"
    print("\n✨ User Name:", name)

    # Extract Education from the response
    education_match = re.search(r'### Education\s*(.*?)(?=###|$)', suggestion, re.DOTALL)
    education = education_match.group(1).strip() if education_match else "Education not found"
    print("📚 Education:", education)

    # Extract Target Role from the very top if present
    top_role_match = re.search(r'^\*\*Target Role:\*\*\s*(.+)$', suggestion, re.MULTILINE)
    if top_role_match:
        target_role = top_role_match.group(1).strip()
    else:
        # Fallback: Extract Target Role (if present) from previous logic
        target_role_match = re.search(r'Target (Job )?Role/Title:\s*(.*)', suggestion)
        target_role = target_role_match.group(2).strip() if target_role_match else ""
    print("🎯 Target Role:", target_role)

    # Extract Current Profile Score (before improvements) from API response
    score_match = re.search(r'##\s*Current Profile Score.*?\*\*Score:\*\*\s*(\d+)', suggestion, re.DOTALL)
    previous_score = int(score_match.group(1)) if score_match else 0

    # Extract New Score After Improvements (final profile score) from API response
    final_score_match = re.search(r'##\s*[⭐️\*]*\s*Final Profile Score.*?\*\*Score:\*\*\s*(\d+)', suggestion, re.DOTALL)
    current_score = int(final_score_match.group(1)) if final_score_match else previous_score

    # Extract rationale from the Current Profile Score section
    rationale_match = re.search(r'##\s*Current Profile Score.*?Rationale:\s*(.*?)(?:\n\s*[-*]|\n\s*Score:|\n\s*$)', suggestion, re.DOTALL)
    rationale = rationale_match.group(1).strip() if rationale_match else ""

    # Clean the rationale to remove any headings like '## Section-by-Section Audit' or '### Profile Summary (About)'
    if rationale:
        rationale = re.split(r'\n+## |\n+### ', rationale)[0].strip()
        rationale = rationale.replace('**', '')

    # Calculate improvement
    improvement = current_score - previous_score

    # --- Robust Section-by-Section Parsing ---
    # 1. Extract the Section-by-Section Audit block
    section_audit = re.search(r'## Section-by-Section Audit(.*?)## Rebuilt Profile', suggestion, re.DOTALL)
    section_text = section_audit.group(1) if section_audit else ""
    if not section_text:
        section_audit = re.search(r'## Section-by-Section Audit(.*)', suggestion, re.DOTALL)
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
        def extract_field(label, text):
            # Match **Label:** (possibly with extra spaces, possibly on same line)
            m = re.search(rf'\*\*{label}:\*\*\s*(.*?)(?=\n\*\*|\Z)', text, re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else "No information provided."

        weaknesses = extract_field("Weaknesses", rest)
        suggestions = extract_field("Suggestions", rest)
        rewritten = extract_field("Rewritten Example", rest)

        # Split weaknesses/suggestions into lists
        weaknesses_list = [w.strip('- ').strip() for w in weaknesses.split('\n') if w.strip()]
        suggestions_list = [s.strip('- ').strip() for s in suggestions.split('\n') if s.strip()]

        sections.append({
            'title': title,
            'weaknesses': weaknesses_list or ["No information provided."],
            'suggestions': suggestions_list or ["No information provided."],
            'rewritten': rewritten or "No rewritten example available."
        })

    # If sections is empty, fill with all required sections as placeholders
    if not sections:
        required_sections = [
            'Profile Summary (About)', 'Headline', 'Experience', 'Skills', 'Education', 'Projects', 'Certifications',
            'Awards & Accomplishments', 'Courses', 'Publications', 'Licenses', 'Volunteering', 'Organizations',
            'Recommendations', 'Languages', 'Interests', 'Any other relevant section'
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
        'Recommendations', 'Languages', 'Interests', 'Any other relevant section'
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
        rebuilt_match = re.search(pattern, suggestion, re.DOTALL)
        if rebuilt_match:
            rebuilt_text = rebuilt_match.group(1).strip()
            break
    
    # If no pattern matched, try to extract anything after "Rebuilt Profile" section
    if not rebuilt_text:
        rebuilt_match = re.search(r'## Rebuilt Profile(.*)', suggestion, re.DOTALL)
        if rebuilt_match:
            rebuilt_text = rebuilt_match.group(1).strip()
            # Remove any trailing sections
            rebuilt_text = re.split(r'\n##\s*[⭐️\*]*\s*Final Profile Score', rebuilt_text)[0]
            rebuilt_text = re.split(r'\n##\s*New Score After Improvements', rebuilt_text)[0]

    # Use the full rebuilt profile text for the summary (so the preview shows all sections)
    summary = rebuilt_text

    rebuilt_profile = {
        'summary': summary,
        'experience': [],
        'projects': [],
        'skills': [],
        'education': [],
        'certifications': [],
        'awards': [],
        'languages': [],
        'interests': [],
    }

   

    # Extract remarks from the Final Profile Score section
    remarks_match = re.search(r'##\s*[⭐️\*]*\s*Final Profile Score.*?\*\*Remarks:\*\*\s*(.*?)(?:\n|$)', suggestion, re.DOTALL)
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

if __name__ == '__main__':
    # Run the Flask app on all interfaces for Docker/VM compatibility
    app.run(debug=True, host='0.0.0.0')
