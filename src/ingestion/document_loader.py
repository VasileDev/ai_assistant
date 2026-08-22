# Loading the pdf file 

from pdfreader import SimplePDFViewer

def load_pdf(pdf_name: str) -> list[str]:
    with open(pdf_name, 'rb') as pdf:
        viewer = SimplePDFViewer(pdf)
        pdf_text = []

        for canvas in viewer:
            content = " ".join(canvas.strings)
            pdf_text.append(content)

    return pdf_text
