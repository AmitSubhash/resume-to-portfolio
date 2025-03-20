import os
import json
import re
import PyPDF2
import pdfplumber
import docx
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# Create a directory to store uploaded files
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

###############################################################################
# Text Extraction
###############################################################################

def extract_text_pdf(file_path):
    """
    Improved PDF extraction using pdfplumber
    """
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_docx(file_path):
    """
    Extract text from a DOCX file using the python-docx library
    """
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs)

###############################################################################
# JSON Validation
###############################################################################

def validate_json_structure(data):
    """Ensure required fields exist with proper types."""
    structure = {
        "name": str,
        "email": str,
        "phone": str,
        "linkedin": str,
        "location": str,
        "openToRelocation": bool,
        "education": list,
        "skills": list,
        "workExperience": list,
        "projects": list,
        "achievements": list
    }
    
    for key, typ in structure.items():
        if key not in data:
            raise KeyError(f"Missing required field: {key}")
        if not isinstance(data[key], typ):
            raise TypeError(f"Field '{key}' should be {typ.__name__}, got {type(data[key])}")

def extract_json(text):
    """
    Extract JSON from raw text by locating the first '{' and the last '}'.
    Also remove any stray ```json or ``` that might be around it.
    """
    # Remove possible markdown fences
    text = text.replace('```json', '').replace('```', '')

    start = text.find('{')
    end = text.rfind('}') + 1

    if start == -1 or end == 0:
        raise ValueError("Failed to locate valid JSON delimiters '{' and '}' in the response.")

    json_str = text[start:end]
    return json_str

###############################################################################
# Prompt and LLM
###############################################################################

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

def call_llm_for_gatsby_metadata(resume_text: str) -> str:
    # Minimal prompt example (adapt as needed)
    prompt = f"""
Convert the following resume text into valid JSON for Gatsby siteMetadata (no extra fields, no markdown):
{{
  "siteUrl": "https://example.com" (if you cannot find this replace with https://memory.toys/classic/easy/),
  "name": "John Doe",
  "title": "John Doe | Software Engineer",
  "description": "Short summary of professional background",
  "author": "@twitter_handle_if_any",
  "github": "https://github.com/username",
  "linkedin": "https://linkedin.com/in/username",
  "about": "Short personal bio here"() here take the resume data you have and generate 3 and write it excaple, Curious.Persistent.Grit.),
  "projects": [
    {{
      "name": "Project Name",
      "description": "Short project description",
      "link": "https://project-link.com"
    }}
  ],
  "experience": [
    {{
      "name": "Company/Organization",
      "description": "Role, Start Date - End Date",
      "link": "https://company-link.com"
    }}
  ],
  "skills": [
    {{
      "name": "Skill/Category",
      "description": "Short explanation"
    }}
  ]
}}

Resume Text:
{resume_text}

Output ONLY valid JSON:
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="mixtral-8x7b-32768",  # Replace with desired model
        temperature=0.2,
        max_tokens=2000
    )

    # Return the raw text of the model's message (which should be JSON)
    return response.choices[0].message.content

