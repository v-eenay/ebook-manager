"""
PDF Reader
Handles PDF document reading and rendering using PyMuPDF.
"""

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Qt imports will be handled by the main application
# This reader only handles raw image data, not QPixmap creation

from .base_reader import BaseReader


class PDFReader(BaseReader):
    """PDF document reader using PyMuPDF."""
    
    def __init__(self):
        super().__init__()
        self.document = None

        # Lazy logger import to avoid side-effects on import
        try:
            from utils.logger import setup_logging
            self.logger = setup_logging()
        except Exception:
            import logging
            self.logger = logging.getLogger("ebook_reader")

        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is required for PDF support. Install with: pip install PyMuPDF")
            
    def load(self, file_path: str) -> bool:
        """Load a PDF document."""
        try:
            self.logger.info("Opening PDF: %s", file_path)
            self.document = fitz.open(file_path)
            self.file_path = file_path
            self.page_count = len(self.document)
            self.is_loaded = True

            # Extract metadata
            metadata = self.document.metadata
            self.metadata = {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
            }
            self.logger.info("PDF loaded: %s (%d pages)", file_path, self.page_count)

            return True

        except Exception as e:
            self.close()
            self.logger.exception("Failed to load PDF %s: %s", file_path, e)
            raise Exception(f"Failed to load PDF: {str(e)}")
            
    def get_page_image_data(self, page_index: int) -> tuple:
        """Get page image data and dimensions for display."""
        if not self.is_loaded or not self.document:
            raise RuntimeError("No document loaded")

        if page_index < 0 or page_index >= self.page_count:
            raise IndexError(f"Page index {page_index} out of range (0-{self.page_count-1})")

        try:
            # Get the page
            page = self.document[page_index]

            # Render the page to a pixmap with good quality
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)

            # Get image data and dimensions (use PNG for Qt compatibility)
            img_data = pix.tobytes("png")
            width = pix.width
            height = pix.height

            return img_data, width, height

        except Exception as e:
            raise Exception(f"Failed to render page {page_index}: {str(e)}")

    def get_page_data(self, page_index: int) -> bytes:
        """Get raw page image data (for backward compatibility)."""
        img_data, _, _ = self.get_page_image_data(page_index)
        return img_data

    def get_page(self, page_index: int):
        """Get page content (implementation of abstract method)."""
        # Return image data for PDF pages
        return self.get_page_image_data(page_index)

    def get_page_count(self) -> int:
        """Get the total number of pages."""
        return self.page_count if self.is_loaded else 0
        
    def get_page_text(self, page_index: int) -> str:
        """Get the text content of a page."""
        if not self.is_loaded or not self.document:
            raise RuntimeError("No document loaded")
            
        if page_index < 0 or page_index >= self.page_count:
            raise IndexError(f"Page index {page_index} out of range")
            
        try:
            page = self.document[page_index]
            return page.get_text()
        except Exception as e:
            raise Exception(f"Failed to extract text from page {page_index}: {str(e)}")
            
    def search_text(self, query: str, page_index: int = None) -> list:
        """Search for text in the document."""
        if not self.is_loaded or not self.document:
            raise RuntimeError("No document loaded")
            
        results = []
        
        if page_index is not None:
            # Search in specific page
            if 0 <= page_index < self.page_count:
                page = self.document[page_index]
                text_instances = page.search_for(query)
                for inst in text_instances:
                    results.append({
                        'page': page_index,
                        'bbox': inst,
                        'text': query
                    })
        else:
            # Search in all pages
            for i in range(self.page_count):
                page = self.document[i]
                text_instances = page.search_for(query)
                for inst in text_instances:
                    results.append({
                        'page': i,
                        'bbox': inst,
                        'text': query
                    })
                    
        return results
        
    def close(self):
        """Close the PDF document."""
        if self.document:
            self.document.close()
            self.document = None
        super().close()
