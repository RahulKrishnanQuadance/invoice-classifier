import os
import openai
import pdfplumber
from PyPDF2 import PdfWriter, PdfReader

# === CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables")
openai.api_key = OPENAI_API_KEY

# === OUTPUT DIRECTORY ===
output_dir = "output_pdfs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
print(f"Output directory: {output_dir}")

# === FUNCTIONS ===
def classify_page(text):
    prompt = f"""
    Identify the pages in Document in a way that is easy to understand for a general audience 
    and classify each page by type (e.g., Invoice, Purchase Order, Delivery Note, Unknown). 
    Group the pages under their respective classifications using headings.

    Page content:
    {text[:2000]}  # limit to 2000 chars
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Unknown"

def split_and_classify(input_pdf, output_dir):
    page_groups = {}

    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")

    print(f"Processing file: {input_pdf}")

    # Step 1: Extract text & classify
    with pdfplumber.open(input_pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            classification = classify_page(text)
            print(f"Page {i+1}: Classified as {classification}")

            if classification not in page_groups:
                page_groups[classification] = []
            page_groups[classification].append(i)

    # Step 2: Write grouped PDFs
    for classification, pages in page_groups.items():
        writer = PdfWriter()
        pdf_reader = PdfReader(input_pdf)
        for p in pages:
            writer.add_page(pdf_reader.pages[p])

        output_path = os.path.join(output_dir, f"{classification}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Saved {output_path}")

# === MAIN ===
if __name__ == "__main__":
    try:
        input_file = "invoice.pdf"  # input PDF from GitHub workflow
        split_and_classify(input_file, output_dir)
        print("✅ Classification completed successfully")
    except Exception as e:
        print(f"❌ Script failed: {e}")
        raise
