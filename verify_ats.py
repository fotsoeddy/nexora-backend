import os
import sys

# Add the project directory to sys.path
sys.path.append('/home/eddy/projects/rochinel/nexora-backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexora_backend.settings')
import django
django.setup()

from ai.utils.cv import extract_text_from_cv
from ai.utils.openai import scan_cv_openai, match_cv_to_job_openai
from ai.models import Job
import io

def test_cv_extraction_mock():
    print("Testing CV extraction mock...")
    # Mock a text file since we can't easily generate a real PDF/DOCX here without more tools
    mock_file = io.BytesIO(b"John Doe\nSoftware Engineer\nPython, Django, React")
    text = extract_text_from_cv(mock_file, "resume.txt")
    print(f"Extracted text: {text}")
    assert "John Doe" in text
    print("CV extraction mock passed!")

def test_openai_utils_mock():
    print("\nTesting OpenAI utils with mock responses (if API key missing)...")
    cv_text = "John Doe, Software Engineer with 5 years of experience in Python."
    
    # Test scan_cv_openai
    scan_result = scan_cv_openai(cv_text)
    print(f"Scan result: {scan_result}")
    assert "score" in scan_result
    
    # Test match_cv_to_job_openai
    match_result = match_cv_to_job_openai(cv_text, "Senior Developer", "Looking for a Python expert with 5 years experience.")
    print(f"Match result: {match_result}")
    assert "match_score" in match_result
    print("OpenAI utils mock tests passed!")

if __name__ == "__main__":
    try:
        test_cv_extraction_mock()
        test_openai_utils_mock()
        print("\nAll verification checks passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)
