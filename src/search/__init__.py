"""
Advanced Search and Indexing Module
Provides full-text search capabilities for the Modern EBook Reader
"""

from .search_engine import SearchEngine
from .indexer import DocumentIndexer
from .search_ui import SearchWidget

__all__ = ['SearchEngine', 'DocumentIndexer', 'SearchWidget']