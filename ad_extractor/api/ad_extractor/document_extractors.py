import pdfplumber
from pathlib import Path
from typing import Optional, Protocol

class TextExtractor(Protocol):
    def extract(self, pdf_path: Path) -> str:
        ...

class PdfPlumberExtractor:
    def extract(self, pdf_path: Path) -> str:        
        text_parts: list[str] = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")

        return "\n\n".join(text_parts)
    
class OCRExtractor:
    def extract(self, pdf_path: Path) -> str:
        #if you have case that need ocr put it here. Make new strategy for OCRTextExtraction
        #Becasue in the assignment there is no need for this case, I leave it as a placeholder
        pass


class PDFExtractorFactory:
    def __init__(
            self, 
            extractor_strategy: Optional[TextExtractor] = PdfPlumberExtractor()
        ):
        self._extractor = extractor_strategy


    def extract_text(self, pdf_path: Path | str) -> str:
        """
            Method to extract text from a single PDF file.
        """
        path = Path(pdf_path) if isinstance(pdf_path, str) else pdf_path
        return self._extractor.extract(path)
    
    def bulk_extract(self, pdf_directory: Path | str) -> dict[str, str]:
        """
            Method to extract text from all PDF files in a given directory.
        """
        dir_path = Path(pdf_directory) if isinstance(pdf_directory, str) else pdf_directory
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")
        
        extracted_texts: dict[str, str] = {}
        
        for pdf_file in dir_path.glob("*.pdf"):
            extracted_texts[pdf_file.name] = self.extract_text(pdf_file)
        
        return extracted_texts