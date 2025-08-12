"""
Annotation Manager - Central coordinator for all annotation operations
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from .models import (
    Annotation, Bookmark, Highlight, Note, AnnotationCategory,
    AnnotationType, AnnotationFilter, AnnotationSearchResult,
    Point, TextSelection
)
from .annotation_storage import AnnotationStorage
from .bookmark_manager import BookmarkManager
from .highlight_manager import HighlightManager
from .note_manager import NoteManager

logger = logging.getLogger("ebook_reader")

class AnnotationManager:
    """Central coordinator for all annotation operations"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize annotation manager with storage"""
        self.storage = AnnotationStorage(storage_path)
        
        # Initialize specialized managers
        self.bookmark_manager = BookmarkManager(self.storage)
        self.highlight_manager = HighlightManager(self.storage)
        self.note_manager = NoteManager(self.storage)
        
        logger.info("Annotation manager initialized")
    
    # Bookmark operations
    def create_bookmark(self, document_path: str, page_number: int, 
                       title: str = "", description: str = "",
                       position: Optional[Point] = None,
                       category: str = "default") -> Optional[Bookmark]:
        """Create a new bookmark"""
        return self.bookmark_manager.create_bookmark(
            document_path, page_number, title, description, position, category
        )
    
    def get_bookmarks(self, document_path: str, page_number: Optional[int] = None) -> List[Bookmark]:
        """Get bookmarks for a document or page"""
        return self.bookmark_manager.get_bookmarks(document_path, page_number)
    
    def update_bookmark(self, bookmark: Bookmark) -> bool:
        """Update an existing bookmark"""
        return self.bookmark_manager.update_bookmark(bookmark)
    
    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Delete a bookmark"""
        return self.bookmark_manager.delete_bookmark(bookmark_id)
    
    # Highlight operations
    def create_highlight(self, document_path: str, page_number: int,
                        text_selection: TextSelection, color: str,
                        note: str = "", category: str = "default") -> Optional[Highlight]:
        """Create a new highlight"""
        return self.highlight_manager.create_highlight(
            document_path, page_number, text_selection, color, note, category
        )
    
    def get_highlights(self, document_path: str, page_number: Optional[int] = None) -> List[Highlight]:
        """Get highlights for a document or page"""
        return self.highlight_manager.get_highlights(document_path, page_number)
    
    def update_highlight(self, highlight: Highlight) -> bool:
        """Update an existing highlight"""
        return self.highlight_manager.update_highlight(highlight)
    
    def delete_highlight(self, highlight_id: str) -> bool:
        """Delete a highlight"""
        return self.highlight_manager.delete_highlight(highlight_id)
    
    def change_highlight_color(self, highlight_id: str, new_color: str) -> bool:
        """Change the color of a highlight"""
        return self.highlight_manager.change_color(highlight_id, new_color)
    
    # Note operations
    def create_note(self, document_path: str, page_number: int,
                   position: Point, content: str, plain_text: str = "",
                   category: str = "default",
                   parent_note_id: Optional[str] = None) -> Optional[Note]:
        """Create a new note"""
        return self.note_manager.create_note(
            document_path, page_number, position, content, plain_text, category, parent_note_id
        )
    
    def get_notes(self, document_path: str, page_number: Optional[int] = None) -> List[Note]:
        """Get notes for a document or page"""
        return self.note_manager.get_notes(document_path, page_number)
    
    def update_note(self, note: Note) -> bool:
        """Update an existing note"""
        return self.note_manager.update_note(note)
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        return self.note_manager.delete_note(note_id)
    
    # General annotation operations
    def get_all_annotations(self, document_path: str, 
                           page_number: Optional[int] = None) -> List[Annotation]:
        """Get all annotations for a document or page"""
        annotations = []
        
        # Get all annotation types
        annotations.extend(self.get_bookmarks(document_path, page_number))
        annotations.extend(self.get_highlights(document_path, page_number))
        annotations.extend(self.get_notes(document_path, page_number))
        
        # Sort by creation time
        annotations.sort(key=lambda a: a.created_at)
        
        return annotations
    
    def get_annotation_by_id(self, annotation_id: str) -> Optional[Annotation]:
        """Get a specific annotation by ID"""
        return self.storage.load_annotation(annotation_id)
    
    def delete_annotation(self, annotation_id: str) -> bool:
        """Delete any annotation by ID"""
        return self.storage.delete_annotation(annotation_id)
    
    def search_annotations(self, query: str, filters: Optional[AnnotationFilter] = None,
                          limit: int = 100) -> List[AnnotationSearchResult]:
        """Search annotations with optional filters"""
        return self.storage.search_annotations(query, filters, limit)
    
    # Category operations
    def get_categories(self) -> List[AnnotationCategory]:
        """Get all annotation categories"""
        return self.storage.get_categories()
    
    def create_category(self, name: str, color: str, description: str = "") -> Optional[AnnotationCategory]:
        """Create a new annotation category"""
        category = AnnotationCategory(name=name, color=color, description=description)
        
        if self.storage.save_category(category):
            logger.info(f"Created category: {name}")
            return category
        
        return None
    
    def update_category(self, category: AnnotationCategory) -> bool:
        """Update an existing category"""
        return self.storage.save_category(category)
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        return self.storage.delete_category(category_id)
    
    def assign_category(self, annotation_id: str, category: str) -> bool:
        """Assign an annotation to a category"""
        annotation = self.get_annotation_by_id(annotation_id)
        if annotation:
            annotation.category = category
            return self.storage.save_annotation(annotation)
        return False
    
    # Bulk operations
    def delete_annotations_by_document(self, document_path: str) -> int:
        """Delete all annotations for a document"""
        annotations = self.get_all_annotations(document_path)
        deleted_count = 0
        
        for annotation in annotations:
            if self.delete_annotation(annotation.id):
                deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} annotations for document: {document_path}")
        return deleted_count
    
    def export_annotations(self, document_path: str, format: str = "json") -> Optional[str]:
        """Export annotations for a document"""
        try:
            annotations = self.get_all_annotations(document_path)
            
            if format.lower() == "json":
                import json
                data = {
                    "document_path": document_path,
                    "export_timestamp": str(datetime.now()),
                    "annotations": [ann.to_dict() for ann in annotations],
                    "categories": [cat.to_dict() for cat in self.get_categories()]
                }
                return json.dumps(data, indent=2)
            
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    "ID", "Type", "Page", "Category", "Content", "Created", "Updated"
                ])
                
                # Write annotations
                for ann in annotations:
                    writer.writerow([
                        ann.id,
                        ann.get_type().value,
                        ann.page_number,
                        ann.category,
                        ann.get_display_text(),
                        ann.created_at.isoformat(),
                        ann.updated_at.isoformat()
                    ])
                
                return output.getvalue()
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to export annotations: {e}")
            return None
    
    def import_annotations(self, data: str, format: str = "json") -> bool:
        """Import annotations from exported data"""
        try:
            if format.lower() == "json":
                import json
                parsed_data = json.loads(data)
                
                # Import categories first
                if "categories" in parsed_data:
                    for cat_data in parsed_data["categories"]:
                        category = AnnotationCategory.from_dict(cat_data)
                        self.storage.save_category(category)
                
                # Import annotations
                if "annotations" in parsed_data:
                    for ann_data in parsed_data["annotations"]:
                        ann_type = AnnotationType(ann_data.get("type", "bookmark"))
                        
                        if ann_type == AnnotationType.BOOKMARK:
                            annotation = Bookmark.from_dict(ann_data)
                        elif ann_type == AnnotationType.HIGHLIGHT:
                            annotation = Highlight.from_dict(ann_data)
                        elif ann_type == AnnotationType.NOTE:
                            annotation = Note.from_dict(ann_data)
                        else:
                            continue
                        
                        self.storage.save_annotation(annotation)
                
                logger.info("Annotations imported successfully")
                return True
            
            else:
                logger.error(f"Unsupported import format: {format}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to import annotations: {e}")
            return False
    
    def get_statistics(self, document_path: Optional[str] = None) -> Dict[str, Any]:
        """Get annotation statistics"""
        return self.storage.get_annotation_stats(document_path)
    
    def backup_annotations(self, backup_path: str) -> bool:
        """Create a backup of all annotations"""
        return self.storage.backup_annotations(backup_path)
    
    def restore_annotations(self, backup_path: str) -> bool:
        """Restore annotations from backup"""
        return self.storage.restore_annotations(backup_path)
    
    def cleanup_orphaned_annotations(self) -> int:
        """Remove annotations for documents that no longer exist"""
        # This would require checking file system for document existence
        # Implementation depends on how document paths are managed
        # For now, return 0 as placeholder
        return 0