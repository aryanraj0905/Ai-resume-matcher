import fitz  # PyMuPDF


class PDFParsingError(Exception):
    """Raised when a PDF cannot be parsed into usable resume text."""


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF resume.

    Parameters:
        pdf_path (str): Path to the uploaded PDF.

    Returns:
        str: Complete text extracted from the PDF.
    """

    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except (FileNotFoundError, fitz.FileDataError, fitz.EmptyFileError) as exc:
        raise PDFParsingError("Invalid or unreadable PDF file.") from exc

    try:
        if document.is_encrypted:
            raise PDFParsingError("Encrypted PDF files are not supported.")

        text = ""

        for page in document:
            text += page.get_text()

        text = text.strip()

        if not text:
            raise PDFParsingError("No readable text found in the PDF.")

        return text
    finally:
        document.close()
