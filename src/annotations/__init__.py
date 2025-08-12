"""
Annotations Module for Modern EBook Reader
Provides comprehensive bookmark, highlight, and note functionality
"""

from .annotation_manager import AnnotationManager
from .bookmark_manager import BookmarkManager
from .highlight_manager import HighlightManager
from .note_manager import NoteManager
from .annotation_storage import AnnotationStorage
from .models import Annotation, Bookmark, Highlight, Note, AnnotationCategory

__all__ = [
    'AnnotationManager',
    'BookmarkManager', 
    'HighlightManager',
    'NoteManager',
    'AnnotationStorage',
    'Annotation',
    'Bookmark',
    'Highlight', 
    'Note',
    'AnnotationCategory'
]