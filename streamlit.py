import streamlit as st
import docx2txt
import PyPDF2
from groq import Groq
import PyPDF2
from backend import extract_resume, gatsby_builder

st.title("Upload Your Resume")

uploaded_file = st.file_uploader(
    "Upload your resume (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"]
)

extracted_text = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        # PDF extraction
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text_pages = [page.extract_text() for page in pdf_reader.pages]
        extracted_text = "\n".join(text_pages)

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # DOCX extraction
        extracted_text = docx2txt.process(uploaded_file)

    elif uploaded_file.type == "text/plain":
        # TXT extraction
        extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")

    else:
        st.error("Unsupported file format.")

# Display the extracted text if any, and start converting into structured data
if extracted_text:
    st.write("## Extracted Resume Text:")
    st.text_area("Preview:", extracted_text, height=250)

    extracted_json = extract_resume.call_llm_for_gatsby_metadata(extracted_text)

    if extracted_json:
        # DEBUG:
        st.write("## Extracted JSON:")
        st.text_area("Preview:", extracted_json, height=250)

        gatsby_builder.create_gatsby_project(extracted_json)


