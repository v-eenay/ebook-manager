"""
Document Manager
Handles loading and managing different document types.
"""

import os
from pathlib import Path
from typing import Optional, Union

from .pdf_reader import PDFReader
from .epub_reader import EPUBReader
from .mobi_reader import MOBIReader


class DocumentManager:
    """Manages document loading and provides a unified interface."""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': PDFReader,
            '.epub': EPUBReader,
            '.mobi': MOBIReader,
        }
        
    def is_supported(self, file_path: Union[str, Path]) -> bool:
        """Check if the file format is supported."""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats
        
    def load_document(self, file_path: Union[str, Path]) -> Optional[object]:
        """Load a document and return the appropriate reader instance."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not self.is_supported(file_path):
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
        # Get the appropriate reader class
        reader_class = self.supported_formats[file_path.suffix.lower()]
        
        # Create and initialize the reader
        reader = reader_class()
        reader.load(str(file_path))
        
        return reader
        
    def get_supported_formats(self) -> list:
        """Get a list of supported file formats."""
        return list(self.supported_formats.keys())
        
    def get_format_description(self) -> str:
        """Get a human-readable description of supported formats."""
        formats = [fmt.upper().lstrip('.') for fmt in self.supported_formats.keys()]
        return ", ".join(formats)
