import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str):
    """
    Extract all text from a PDF resume.

    Parameters:
        pdf_path (str): Path to the uploaded PDF.

    Returns:
        str: Complete text extracted from the PDF.
    """

    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text
    
    