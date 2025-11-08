from transformers import pipeline
import pdfplumber
import pdfplumber, re
import pypdf

import re

def clean_text(text: str) -> str:
    text = re.sub(r"(?<=\w)([A-Z])", r" \1", text)   # insert space before capital letters that follow lowercase
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text) # fix run-together words
    text = re.sub(r"(\d)([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z])([a-z])", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)                  # collapse multiple spaces
    return text.strip()

def add_section_breaks(text: str) -> str:
    # Add newlines before section headers
    text = re.sub(r"(Task \d+:)", r"\n\n\1\n", text)
    text = re.sub(r"(Section \d+|Introduction|Conclusion|Report|Marking Guidelines)", r"\n\n\1\n", text)
    return text


def extract_relevant_sections(text: str) -> str:
    sections = []
    for paragraph in text.split("\n\n"):
        if any(keyword.lower() in paragraph.lower() for keyword in ["deliverable", "deadline", "mark", "submission"]):
            sections.append(paragraph)
    return "\n\n".join(sections)



def load_and_prepare_pdf(path):
    with pdfplumber.open(path) as pdf:
        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    cleaned = clean_text(raw_text)
    structured = add_section_breaks(cleaned)
    focused = extract_relevant_sections(structured)
    return focused or structured


# 2. read PDF

file_path = "/Users/jonathancrocker/Downloads/MLP2025_26_CW1_Spec.pdf"
# importing all the required modules

# creating a pdf reader object
reader = pypdf.PdfReader(file_path)

# print the number of pages in pdf file
print(len(reader.pages))

# print the text of the first page
print(reader.pages[0].extract_text())

# 1. load model
extractor = pipeline("text2text-generation", model="google/flan-t5-base")

# 3. prompt
prompt = f"""
You are an assistant that analyses coursework project specifications.

Your goal is to extract key information and return it clearly in bullet points.

**Instructions**
- Do NOT repeat the original text.
- Use short, clear bullet points.
- Group similar items together logically.
- Follow this format:

Deliverables:
• ...
• ...

Deadlines:
• ...
• ...

Marking Criteria:
• ...
• ...

Constraints:
• ...
• ...

Coursework Description:
{text}
"""

# 4. run
# result = extractor(prompt, temperature=0.2)[0]["generated_text"]
# print(result)
# print(len(result))

print(text)
