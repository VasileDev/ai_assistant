from pypdf import PdfReader

# loads the pdf into the program by creating a list containing each page as an ellement
def load_pdf(pdf_name: str)->list[str]:
    reader = PdfReader(pdf_name)
    content_of_document = []
    
    for page in reader.pages:
        text = page.extract_text() or ""
        content_of_document.append(text)

    return content_of_document
