# Loading the pdf file 

# from pdfreader import SimplePDFViewer

from pypdf import PdfReader

# pdfreader option
# def load_pdf(pdf_name: str) -> list[str]:
#     with open(pdf_name, 'rb') as pdf:
#         viewer = SimplePDFViewer(pdf)
#         pdf_text = []

#         for canvas in viewer:
#             content = "".join(canvas.strings)
#             pdf_text.append(content)

#     return pdf_text

# add pypdf to requirements

# returns a list of strings, each element of the list is a page of the pdf uploaded
def load_pdf(pdf_name:str)->list[str]:
    reader = PdfReader(pdf_name)
    content_of_document = []
    
    for page in reader.pages:
        text = page.extract_text() or ""
        content_of_document.append(text)

    return content_of_document
    