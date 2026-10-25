from app.application.ports.rag.loader import AbstractDocumentLoader
from langchain_community.document_loaders import PyMuPDFLoader


class PDFLoader(AbstractDocumentLoader):
    def __init__(self):
        pass
    
    supported_extension = "pdf"
    async def load(self, file_path):
        pdf_loader = PyMuPDFLoader(str(file_path))
        return await pdf_loader.aload()
