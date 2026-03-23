import pdfplumber
import docx
import io

def extract_text_from_pdf(file_obj):
    """
    Extracts text from a PDF file object.
    """
    text = ""
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_obj):
    """
    Extracts text from a DOCX file object.
    """
    doc = docx.Document(file_obj)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_cv(file_obj, filename):
    """
    Generalized function to extract text based on file extension.
    """
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_obj)
    elif filename.lower().endswith('.docx'):
        return extract_text_from_docx(file_obj)
    elif filename.lower().endswith('.doc'):
        # Note: .doc is older format, python-docx doesn't support it directly.
        # For now, we'll suggest converting to .docx or .pdf.
        raise ValueError("Unsupported file format: .doc. Please use .pdf or .docx.")
    else:
        # Try to read as plain text if it's not a known binary format
        try:
            file_obj.seek(0)
            return file_obj.read().decode('utf-8')
        except Exception:
            raise ValueError(f"Unsupported file format: {filename}")
