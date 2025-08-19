import os
import sys
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import openai

# Read API key from environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

input_pdf = sys.argv[1]
output_dir = sys.argv[2]

# Ensure output folder exists
os.makedirs(output_dir, exist_ok=True)

# Validate PDF
try:
    reader = PdfReader(input_pdf)
    if len(reader.pages) == 0:
        raise ValueError("PDF has no pages")
except Exception as e:
    print(f"❌ PDF validation failed: {e}")
    sys.exit(1)

def classify_page(text):
    prompt = f"""
    Identify the pages in Document in a way that is easy to understand for a general audience and classify each page by type (e.g., Invoice, Purchase Order, Delivery Note, Unknown). Group the pages under their respective classifications using headings.
    {text[:2000]}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response["choices"][0]["message"]["content"].strip()

# Split and classify
page_groups = {}
with pdfplumber.open(input_pdf) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        classification = classify_page(text)
        page_groups.setdefault(classification, []).append(i)

# Write grouped PDFs
for classification, pages in page_groups.items():
    writer = PdfWriter()
    for p in pages:
        writer.add_page(PdfReader(input_pdf).pages[p])
    output_path = os.path.join(output_dir, f"{classification}.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Saved {output_path}")
