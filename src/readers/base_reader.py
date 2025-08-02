"""
Base Reader Class
Abstract base class for all document readers.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseReader(ABC):
    """Abstract base class for document readers."""
    
    def __init__(self):
        self.file_path: Optional[str] = None
        self.is_loaded: bool = False
        self.page_count: int = 0
        self.metadata: dict = {}
        
    @abstractmethod
    def load(self, file_path: str) -> bool:
        """Load a document from the given file path."""
        pass
        
    @abstractmethod
    def get_page(self, page_index: int) -> Any:
        """Get the content of a specific page (0-based index)."""
        pass
        
    @abstractmethod
    def get_page_count(self) -> int:
        """Get the total number of pages in the document."""
        pass
        
    def get_metadata(self) -> dict:
        """Get document metadata (title, author, etc.)."""
        return self.metadata.copy()
        
    def get_title(self) -> str:
        """Get the document title."""
        return self.metadata.get('title', 'Unknown Title')
        
    def get_author(self) -> str:
        """Get the document author."""
        return self.metadata.get('author', 'Unknown Author')
        
    def is_document_loaded(self) -> bool:
        """Check if a document is currently loaded."""
        return self.is_loaded
        
    def close(self):
        """Close the document and free resources."""
        self.file_path = None
        self.is_loaded = False
        self.page_count = 0
        self.metadata = {}
