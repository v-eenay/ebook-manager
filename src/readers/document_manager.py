"""
Document Manager
Handles loading and managing different document types.
"""

import os
from pathlib import Path
from typing import Optional, Union


class DocumentManager:
    """Manages document loading and provides a unified interface."""

    def __init__(self):
        # Use lazy imports to avoid QPixmap creation during import
        self.supported_formats = {
            '.pdf': 'PDFReader',
            '.epub': 'EPUBReader',
            '.mobi': 'MOBIReader',
        }
        self._reader_classes = {}  # Cache for imported classes
        # Lazy logger import to avoid side-effects on import
        try:
            from utils.logger import setup_logging
            self.logger = setup_logging()
        except Exception:
            import logging
            self.logger = logging.getLogger("ebook_reader")

    def _get_reader_class(self, format_ext: str):
        """Lazily import and return the reader class for the given format."""
        if format_ext not in self._reader_classes:
            class_name = self.supported_formats[format_ext]

            try:
                if class_name == 'PDFReader':
                    from .pdf_reader import PDFReader
                    self._reader_classes[format_ext] = PDFReader
                elif class_name == 'EPUBReader':
                    from .epub_reader import EPUBReader
                    self._reader_classes[format_ext] = EPUBReader
                elif class_name == 'MOBIReader':
                    from .mobi_reader import MOBIReader
                    self._reader_classes[format_ext] = MOBIReader
                else:
                    raise ValueError(f"Unknown reader class: {class_name}")
            except Exception as e:
                self.logger.exception("Failed to import reader for %s: %s", format_ext, e)
                raise

        return self._reader_classes[format_ext]

    def is_supported(self, file_path: Union[str, Path]) -> bool:
        """Check if the file format is supported."""
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats
        
    def load_document(self, file_path: Union[str, Path]) -> Optional[object]:
        """Load a document and return the appropriate reader instance."""
        file_path = Path(file_path)
        self.logger.info("Loading document: %s", file_path)

        if not file_path.exists():
            self.logger.error("File not found: %s", file_path)
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.is_supported(file_path):
            self.logger.error("Unsupported file format: %s", file_path.suffix)
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Get the appropriate reader class (lazy import)
        format_ext = file_path.suffix.lower()
        reader_class = self._get_reader_class(format_ext)

        # Create and initialize the reader
        try:
            reader = reader_class()
            reader.load(str(file_path))
            self.logger.info("Document loaded successfully with %s", reader_class.__name__)
            return reader
        except Exception as e:
            self.logger.exception("Failed to load document %s: %s", file_path, e)
            raise
        
    def get_supported_formats(self) -> list:
        """Get a list of supported file formats."""
        return list(self.supported_formats.keys())
        
    def get_format_description(self) -> str:
        """Get a human-readable description of supported formats."""
        formats = [fmt.upper().lstrip('.') for fmt in self.supported_formats.keys()]
        return ", ".join(formats)
