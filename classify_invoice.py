import os
import openai
import pdfplumber
from PyPDF2 import PdfWriter

openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_page(text):
    prompt = f"""
    Identify the pages in Document in a way that is easy to understand for a general audience and classify each page by type (e.g., Invoice, Purchase Order, Delivery Note, Unknown). Group the pages under their respective classifications using headings. For example:

    Invoice : Page 1
    Purchase Order : Page 4,5,6
    Delivery Note : Page 7 .
    
    Page content:
    {text[:2000]}  # limit to 2000 chars
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response["choices"][0]["message"]["content"].strip()

def split_and_classify(input_pdf, output_dir):
    page_groups = {}

    # Step 1: Extract text & classify
    with pdfplumber.open(input_pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            classification = classify_page(text)

            if classification not in page_groups:
                page_groups[classification] = []
            page_groups[classification].append(i)

    # Step 2: Write grouped PDFs
    for classification, pages in page_groups.items():
        writer = PdfWriter()
        for p in pages:
            writer.add_page(PdfReader(input_pdf).pages[p])

        output_path = os.path.join(output_dir, f"{classification}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Saved {output_path}")

# Example usage
split_and_classify("invoice.pdf", "output_pdfs")
