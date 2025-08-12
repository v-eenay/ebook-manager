"""
Note Manager - Specialized handling of notes and comments
"""

import logging
import re
from typing import List, Optional, Dict
from datetime import datetime

from .models import Note, Point, AnnotationType
from .annotation_storage import AnnotationStorage

logger = logging.getLogger("ebook_reader")

class NoteManager:
    """Specialized manager for note operations"""
    
    def __init__(self, storage: AnnotationStorage):
        """Initialize with storage instance"""
        self.storage = storage
    
    def create_note(self, document_path: str, page_number: int,
                   position: Point, content: str, plain_text: str = "",
                   category: str = "default",
                   parent_note_id: Optional[str] = None) -> Optional[Note]:
        """Create a new note"""
        try:
            # Extract plain text if not provided
            if not plain_text and content:
                plain_text = self._extract_plain_text(content)
            
            # Create note
            note = Note(
                document_path=document_path,
                page_number=page_number,
                position=position,
                content=content,
                plain_text=plain_text,
                category=category,
                parent_note_id=parent_note_id
            )
            
            # Save to storage
            if self.storage.save_annotation(note):
                logger.info(f"Created note on page {page_number}: {plain_text[:50]}...")
                return note
            else:
                logger.error("Failed to save note")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create note: {e}")
            return None
    
    def get_notes(self, document_path: str, 
                 page_number: Optional[int] = None) -> List[Note]:
        """Get notes for a document or specific page"""
        try:
            annotations = self.storage.load_annotations(
                document_path, page_number, AnnotationType.NOTE
            )
            
            # Filter and cast to notes
            notes = [ann for ann in annotations if isinstance(ann, Note)]
            
            # Sort by page number, then by position, then by creation time
            notes.sort(key=lambda n: (n.page_number, n.position.x, n.position.y, n.created_at))
            
            return notes
            
        except Exception as e:
            logger.error(f"Failed to get notes for {document_path}: {e}")
            return []
    
    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID"""
        annotation = self.storage.load_annotation(note_id)
        if annotation and isinstance(annotation, Note):
            return annotation
        return None
    
    def update_note(self, note: Note) -> bool:
        """Update an existing note"""
        try:
            # Update plain text if content changed
            if note.content and not note.plain_text:
                note.plain_text = self._extract_plain_text(note.content)
            
            note.update_timestamp()
            success = self.storage.save_annotation(note)
            
            if success:
                logger.info(f"Updated note: {note.id}")
            else:
                logger.error(f"Failed to update note: {note.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update note {note.id}: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note and its replies"""
        try:
            # First, delete any reply notes
            self._delete_note_replies(note_id)
            
            # Then delete the note itself
            success = self.storage.delete_annotation(note_id)
            
            if success:
                logger.info(f"Deleted note: {note_id}")
            else:
                logger.error(f"Failed to delete note: {note_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete note {note_id}: {e}")
            return False
    
    def create_reply(self, parent_note_id: str, content: str, 
                    plain_text: str = "", category: str = "default") -> Optional[Note]:
        """Create a reply to an existing note"""
        parent_note = self.get_note_by_id(parent_note_id)
        if not parent_note:
            logger.error(f"Parent note not found: {parent_note_id}")
            return None
        
        # Create reply note at the same position as parent
        return self.create_note(
            document_path=parent_note.document_path,
            page_number=parent_note.page_number,
            position=parent_note.position,
            content=content,
            plain_text=plain_text,
            category=category,
            parent_note_id=parent_note_id
        )
    
    def get_note_thread(self, note_id: str) -> List[Note]:
        """Get a note and all its replies in chronological order"""
        note = self.get_note_by_id(note_id)
        if not note:
            return []
        
        # If this is a reply, get the root note
        root_note = note
        if note.parent_note_id:
            root_note = self.get_note_by_id(note.parent_note_id)
            if not root_note:
                root_note = note
        
        # Get all notes for the document
        all_notes = self.get_notes(root_note.document_path)
        
        # Build the thread
        thread = [root_note]
        
        # Find all replies to the root note
        replies = [n for n in all_notes if n.parent_note_id == root_note.id]
        replies.sort(key=lambda n: n.created_at)
        thread.extend(replies)
        
        return thread
    
    def get_note_replies(self, note_id: str) -> List[Note]:
        """Get all direct replies to a note"""
        note = self.get_note_by_id(note_id)
        if not note:
            return []
        
        all_notes = self.get_notes(note.document_path)
        replies = [n for n in all_notes if n.parent_note_id == note_id]
        replies.sort(key=lambda n: n.created_at)
        
        return replies
    
    def move_note(self, note_id: str, new_position: Point, 
                 new_page: Optional[int] = None) -> bool:
        """Move a note to a new position or page"""
        note = self.get_note_by_id(note_id)
        if not note:
            return False
        
        note.position = new_position
        if new_page is not None:
            note.page_number = new_page
        
        return self.update_note(note)
    
    def search_notes(self, document_path: str, query: str) -> List[Note]:
        """Search notes by content"""
        all_notes = self.get_notes(document_path)
        matching_notes = []
        
        query_lower = query.lower()
        
        for note in all_notes:
            # Search in both plain text and content
            if (query_lower in note.plain_text.lower() or 
                query_lower in note.content.lower()):
                matching_notes.append(note)
        
        # Sort by relevance (exact matches first, then by creation date)
        def relevance_score(note):
            text = note.plain_text.lower()
            if query_lower == text:
                return 3  # Exact match
            elif text.startswith(query_lower):
                return 2  # Starts with query
            else:
                return 1  # Contains query
        
        matching_notes.sort(key=lambda n: (-relevance_score(n), n.created_at))
        return matching_notes
    
    def get_notes_by_category(self, document_path: str, category: str) -> List[Note]:
        """Get notes filtered by category"""
        all_notes = self.get_notes(document_path)
        return [n for n in all_notes if n.category == category]
    
    def get_recent_notes(self, document_path: str, limit: int = 10) -> List[Note]:
        """Get most recently created or updated notes"""
        notes = self.get_notes(document_path)
        notes.sort(key=lambda n: max(n.created_at, n.updated_at), reverse=True)
        return notes[:limit]
    
    def get_notes_by_date_range(self, document_path: str, 
                               start_date: datetime, end_date: datetime) -> List[Note]:
        """Get notes created within a date range"""
        all_notes = self.get_notes(document_path)
        return [n for n in all_notes if start_date <= n.created_at <= end_date]
    
    def duplicate_note(self, note_id: str, new_position: Point, 
                      new_page: Optional[int] = None) -> Optional[Note]:
        """Create a duplicate of an existing note"""
        original_note = self.get_note_by_id(note_id)
        if not original_note:
            return None
        
        page = new_page if new_page is not None else original_note.page_number
        
        return self.create_note(
            document_path=original_note.document_path,
            page_number=page,
            position=new_position,
            content=original_note.content,
            plain_text=original_note.plain_text,
            category=original_note.category
        )
    
    def get_note_statistics(self, document_path: str) -> Dict:
        """Get statistics about notes for a document"""
        notes = self.get_notes(document_path)
        
        if not notes:
            return {
                'total_count': 0,
                'by_category': {},
                'with_replies': 0,
                'total_replies': 0,
                'pages_with_notes': [],
                'average_note_length': 0,
                'longest_note': None,
                'most_recent': None
            }
        
        # Count by category
        category_counts = {}
        for note in notes:
            category_counts[note.category] = category_counts.get(note.category, 0) + 1
        
        # Count notes with replies and total replies
        root_notes = [n for n in notes if not n.parent_note_id]
        reply_notes = [n for n in notes if n.parent_note_id]
        notes_with_replies = len(set(n.parent_note_id for n in reply_notes))
        
        # Get pages with notes
        pages_with_notes = sorted(list(set(n.page_number for n in notes)))
        
        # Calculate average note length
        total_length = sum(len(n.plain_text) for n in notes)
        average_length = total_length / len(notes) if notes else 0
        
        # Find longest note
        longest_note = max(notes, key=lambda n: len(n.plain_text)) if notes else None
        
        # Find most recent note
        most_recent = max(notes, key=lambda n: n.created_at) if notes else None
        
        return {
            'total_count': len(notes),
            'by_category': category_counts,
            'with_replies': notes_with_replies,
            'total_replies': len(reply_notes),
            'pages_with_notes': pages_with_notes,
            'average_note_length': round(average_length, 1),
            'longest_note': longest_note.id if longest_note else None,
            'most_recent': most_recent.created_at if most_recent else None
        }
    
    def export_notes(self, document_path: str, include_formatting: bool = True) -> List[dict]:
        """Export notes as a list of dictionaries"""
        notes = self.get_notes(document_path)
        exported = []
        
        for note in notes:
            data = note.to_dict()
            if not include_formatting:
                # Remove HTML content, keep only plain text
                data['content'] = data.get('plain_text', '')
            exported.append(data)
        
        return exported
    
    def import_notes(self, document_path: str, note_data: List[dict]) -> int:
        """Import notes from a list of dictionaries"""
        imported_count = 0
        
        for data in note_data:
            try:
                # Ensure document path matches
                data['document_path'] = document_path
                
                note = Note.from_dict(data)
                if self.storage.save_annotation(note):
                    imported_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to import note: {e}")
                continue
        
        logger.info(f"Imported {imported_count} notes for {document_path}")
        return imported_count
    
    def _extract_plain_text(self, html_content: str) -> str:
        """Extract plain text from HTML content"""
        if not html_content:
            return ""
        
        # Simple HTML tag removal (for basic rich text)
        # In a real implementation, you might want to use a proper HTML parser
        plain_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        plain_text = ' '.join(plain_text.split())
        
        return plain_text
    
    def _delete_note_replies(self, note_id: str):
        """Delete all replies to a note"""
        replies = self.get_note_replies(note_id)
        for reply in replies:
            # Recursively delete replies to replies
            self._delete_note_replies(reply.id)
            self.storage.delete_annotation(reply.id)