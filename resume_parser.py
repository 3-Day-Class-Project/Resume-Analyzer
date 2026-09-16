import pymupdf


def extract_resume_text(pdf_file) -> str:
    """Extract text from a PDF path, bytes value, or Streamlit UploadedFile.

    Streamlit's ``UploadedFile`` is an in-memory file-like object, not the
    path to a file on disk. Opening its bytes avoids PyMuPDF interpreting the
    object as a filename and raising ``FileNotFoundError``.
    """
    if pdf_file is None:
        raise ValueError("No PDF file was provided.")

    if hasattr(pdf_file, "getvalue"):
        pdf_bytes = pdf_file.getvalue()
        document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    elif isinstance(pdf_file, (bytes, bytearray, memoryview)):
        document = pymupdf.open(stream=bytes(pdf_file), filetype="pdf")
    elif hasattr(pdf_file, "read"):
        current_position = pdf_file.tell() if hasattr(pdf_file, "tell") else None
        pdf_bytes = pdf_file.read()
        if current_position is not None and hasattr(pdf_file, "seek"):
            pdf_file.seek(current_position)
        document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    else:
        document = pymupdf.open(pdf_file)

    with document:
        return "\n\n".join(page.get_text() for page in document).strip()
