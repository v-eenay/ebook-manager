"""
Bookmark Manager - Specialized handling of page bookmarks
"""

import logging
from typing import List, Optional
from datetime import datetime

from .models import Bookmark, Point, AnnotationType
from .annotation_storage import AnnotationStorage

logger = logging.getLogger("ebook_reader")

class BookmarkManager:
    """Specialized manager for bookmark operations"""
    
    def __init__(self, storage: AnnotationStorage):
        """Initialize with storage instance"""
        self.storage = storage
    
    def create_bookmark(self, document_path: str, page_number: int,
                       title: str = "", description: str = "",
                       position: Optional[Point] = None,
                       category: str = "default") -> Optional[Bookmark]:
        """Create a new bookmark"""
        try:
            # Generate default title if not provided
            if not title:
                title = f"Page {page_number}"
            
            # Create bookmark
            bookmark = Bookmark(
                document_path=document_path,
                page_number=page_number,
                title=title,
                description=description,
                position=position,
                category=category
            )
            
            # Save to storage
            if self.storage.save_annotation(bookmark):
                logger.info(f"Created bookmark: {title} on page {page_number}")
                return bookmark
            else:
                logger.error(f"Failed to save bookmark: {title}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create bookmark: {e}")
            return None
    
    def get_bookmarks(self, document_path: str, 
                     page_number: Optional[int] = None) -> List[Bookmark]:
        """Get bookmarks for a document or specific page"""
        try:
            annotations = self.storage.load_annotations(
                document_path, page_number, AnnotationType.BOOKMARK
            )
            
            # Filter and cast to bookmarks
            bookmarks = [ann for ann in annotations if isinstance(ann, Bookmark)]
            
            # Sort by page number, then by creation time
            bookmarks.sort(key=lambda b: (b.page_number, b.created_at))
            
            return bookmarks
            
        except Exception as e:
            logger.error(f"Failed to get bookmarks for {document_path}: {e}")
            return []
    
    def get_bookmark_by_id(self, bookmark_id: str) -> Optional[Bookmark]:
        """Get a specific bookmark by ID"""
        annotation = self.storage.load_annotation(bookmark_id)
        if annotation and isinstance(annotation, Bookmark):
            return annotation
        return None
    
    def update_bookmark(self, bookmark: Bookmark) -> bool:
        """Update an existing bookmark"""
        try:
            bookmark.update_timestamp()
            success = self.storage.save_annotation(bookmark)
            
            if success:
                logger.info(f"Updated bookmark: {bookmark.title}")
            else:
                logger.error(f"Failed to update bookmark: {bookmark.title}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update bookmark {bookmark.id}: {e}")
            return False
    
    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Delete a bookmark"""
        try:
            success = self.storage.delete_annotation(bookmark_id)
            
            if success:
                logger.info(f"Deleted bookmark: {bookmark_id}")
            else:
                logger.error(f"Failed to delete bookmark: {bookmark_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete bookmark {bookmark_id}: {e}")
            return False
    
    def bookmark_exists(self, document_path: str, page_number: int) -> bool:
        """Check if a bookmark exists on a specific page"""
        bookmarks = self.get_bookmarks(document_path, page_number)
        return len(bookmarks) > 0
    
    def get_bookmark_for_page(self, document_path: str, page_number: int) -> Optional[Bookmark]:
        """Get the first bookmark for a specific page"""
        bookmarks = self.get_bookmarks(document_path, page_number)
        return bookmarks[0] if bookmarks else None
    
    def toggle_bookmark(self, document_path: str, page_number: int,
                       title: str = "", description: str = "",
                       category: str = "default") -> Optional[Bookmark]:
        """Toggle bookmark on a page (create if doesn't exist, delete if exists)"""
        existing_bookmark = self.get_bookmark_for_page(document_path, page_number)
        
        if existing_bookmark:
            # Delete existing bookmark
            if self.delete_bookmark(existing_bookmark.id):
                logger.info(f"Removed bookmark from page {page_number}")
                return None
            else:
                logger.error(f"Failed to remove bookmark from page {page_number}")
                return existing_bookmark
        else:
            # Create new bookmark
            return self.create_bookmark(
                document_path, page_number, title, description, None, category
            )
    
    def rename_bookmark(self, bookmark_id: str, new_title: str, 
                       new_description: str = "") -> bool:
        """Rename a bookmark"""
        bookmark = self.get_bookmark_by_id(bookmark_id)
        if bookmark:
            bookmark.title = new_title
            bookmark.description = new_description
            return self.update_bookmark(bookmark)
        return False
    
    def move_bookmark(self, bookmark_id: str, new_page: int) -> bool:
        """Move a bookmark to a different page"""
        bookmark = self.get_bookmark_by_id(bookmark_id)
        if bookmark:
            bookmark.page_number = new_page
            return self.update_bookmark(bookmark)
        return False
    
    def get_bookmarks_by_category(self, document_path: str, 
                                 category: str) -> List[Bookmark]:
        """Get bookmarks filtered by category"""
        all_bookmarks = self.get_bookmarks(document_path)
        return [b for b in all_bookmarks if b.category == category]
    
    def get_recent_bookmarks(self, document_path: str, limit: int = 10) -> List[Bookmark]:
        """Get most recently created bookmarks"""
        bookmarks = self.get_bookmarks(document_path)
        bookmarks.sort(key=lambda b: b.created_at, reverse=True)
        return bookmarks[:limit]
    
    def export_bookmarks(self, document_path: str) -> List[dict]:
        """Export bookmarks as a list of dictionaries"""
        bookmarks = self.get_bookmarks(document_path)
        return [bookmark.to_dict() for bookmark in bookmarks]
    
    def import_bookmarks(self, document_path: str, bookmark_data: List[dict]) -> int:
        """Import bookmarks from a list of dictionaries"""
        imported_count = 0
        
        for data in bookmark_data:
            try:
                # Ensure document path matches
                data['document_path'] = document_path
                
                bookmark = Bookmark.from_dict(data)
                if self.storage.save_annotation(bookmark):
                    imported_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to import bookmark: {e}")
                continue
        
        logger.info(f"Imported {imported_count} bookmarks for {document_path}")
        return imported_count
    
    def get_bookmark_statistics(self, document_path: str) -> dict:
        """Get statistics about bookmarks for a document"""
        bookmarks = self.get_bookmarks(document_path)
        
        if not bookmarks:
            return {
                'total_count': 0,
                'by_category': {},
                'pages_with_bookmarks': [],
                'first_bookmark': None,
                'last_bookmark': None
            }
        
        # Count by category
        category_counts = {}
        for bookmark in bookmarks:
            category_counts[bookmark.category] = category_counts.get(bookmark.category, 0) + 1
        
        # Get pages with bookmarks
        pages_with_bookmarks = sorted(list(set(b.page_number for b in bookmarks)))
        
        # Get first and last bookmarks
        bookmarks_by_date = sorted(bookmarks, key=lambda b: b.created_at)
        
        return {
            'total_count': len(bookmarks),
            'by_category': category_counts,
            'pages_with_bookmarks': pages_with_bookmarks,
            'first_bookmark': bookmarks_by_date[0].created_at if bookmarks_by_date else None,
            'last_bookmark': bookmarks_by_date[-1].created_at if bookmarks_by_date else None
        }