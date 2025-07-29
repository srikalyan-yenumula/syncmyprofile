import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file using PyMuPDF.
    Returns the extracted text, or an error message if extraction fails.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {e}" 