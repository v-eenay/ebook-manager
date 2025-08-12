"""
Highlight Manager - Specialized handling of text highlights
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime

from .models import Highlight, TextSelection, Point, AnnotationType, HighlightColor
from .annotation_storage import AnnotationStorage

logger = logging.getLogger("ebook_reader")

class HighlightManager:
    """Specialized manager for highlight operations"""
    
    def __init__(self, storage: AnnotationStorage):
        """Initialize with storage instance"""
        self.storage = storage
    
    def create_highlight(self, document_path: str, page_number: int,
                        text_selection: TextSelection, color: str,
                        note: str = "", category: str = "default") -> Optional[Highlight]:
        """Create a new highlight"""
        try:
            # Validate color
            if not self._is_valid_color(color):
                color = HighlightColor.YELLOW.value
                logger.warning(f"Invalid color provided, using default: {color}")
            
            # Create highlight
            highlight = Highlight(
                document_path=document_path,
                page_number=page_number,
                text_selection=text_selection,
                highlighted_text=text_selection.selected_text,
                color=color,
                note=note,
                category=category
            )
            
            # Save to storage
            if self.storage.save_annotation(highlight):
                logger.info(f"Created highlight on page {page_number}: {text_selection.selected_text[:50]}...")
                return highlight
            else:
                logger.error("Failed to save highlight")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create highlight: {e}")
            return None
    
    def get_highlights(self, document_path: str, 
                      page_number: Optional[int] = None) -> List[Highlight]:
        """Get highlights for a document or specific page"""
        try:
            annotations = self.storage.load_annotations(
                document_path, page_number, AnnotationType.HIGHLIGHT
            )
            
            # Filter and cast to highlights
            highlights = [ann for ann in annotations if isinstance(ann, Highlight)]
            
            # Sort by page number, then by position
            highlights.sort(key=lambda h: (h.page_number, h.text_selection.start_char_index))
            
            return highlights
            
        except Exception as e:
            logger.error(f"Failed to get highlights for {document_path}: {e}")
            return []
    
    def get_highlight_by_id(self, highlight_id: str) -> Optional[Highlight]:
        """Get a specific highlight by ID"""
        annotation = self.storage.load_annotation(highlight_id)
        if annotation and isinstance(annotation, Highlight):
            return annotation
        return None
    
    def update_highlight(self, highlight: Highlight) -> bool:
        """Update an existing highlight"""
        try:
            highlight.update_timestamp()
            success = self.storage.save_annotation(highlight)
            
            if success:
                logger.info(f"Updated highlight: {highlight.id}")
            else:
                logger.error(f"Failed to update highlight: {highlight.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update highlight {highlight.id}: {e}")
            return False
    
    def delete_highlight(self, highlight_id: str) -> bool:
        """Delete a highlight"""
        try:
            success = self.storage.delete_annotation(highlight_id)
            
            if success:
                logger.info(f"Deleted highlight: {highlight_id}")
            else:
                logger.error(f"Failed to delete highlight: {highlight_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete highlight {highlight_id}: {e}")
            return False
    
    def change_color(self, highlight_id: str, new_color: str) -> bool:
        """Change the color of a highlight"""
        if not self._is_valid_color(new_color):
            logger.error(f"Invalid color: {new_color}")
            return False
        
        highlight = self.get_highlight_by_id(highlight_id)
        if highlight:
            highlight.color = new_color
            return self.update_highlight(highlight)
        return False
    
    def add_note_to_highlight(self, highlight_id: str, note: str) -> bool:
        """Add or update a note on a highlight"""
        highlight = self.get_highlight_by_id(highlight_id)
        if highlight:
            highlight.note = note
            return self.update_highlight(highlight)
        return False
    
    def get_highlights_by_color(self, document_path: str, color: str) -> List[Highlight]:
        """Get highlights filtered by color"""
        all_highlights = self.get_highlights(document_path)
        return [h for h in all_highlights if h.color == color]
    
    def get_highlights_by_category(self, document_path: str, category: str) -> List[Highlight]:
        """Get highlights filtered by category"""
        all_highlights = self.get_highlights(document_path)
        return [h for h in all_highlights if h.category == category]
    
    def get_highlights_with_notes(self, document_path: str) -> List[Highlight]:
        """Get highlights that have notes attached"""
        all_highlights = self.get_highlights(document_path)
        return [h for h in all_highlights if h.note.strip()]
    
    def find_overlapping_highlights(self, document_path: str, page_number: int,
                                   text_selection: TextSelection) -> List[Highlight]:
        """Find highlights that overlap with the given text selection"""
        page_highlights = self.get_highlights(document_path, page_number)
        overlapping = []
        
        for highlight in page_highlights:
            if self._selections_overlap(highlight.text_selection, text_selection):
                overlapping.append(highlight)
        
        return overlapping
    
    def merge_highlights(self, highlight_ids: List[str], new_color: str = None) -> Optional[Highlight]:
        """Merge multiple highlights into one"""
        if len(highlight_ids) < 2:
            logger.error("Need at least 2 highlights to merge")
            return None
        
        try:
            # Get all highlights
            highlights = []
            for highlight_id in highlight_ids:
                highlight = self.get_highlight_by_id(highlight_id)
                if highlight:
                    highlights.append(highlight)
            
            if len(highlights) < 2:
                logger.error("Could not load highlights for merging")
                return None
            
            # Ensure all highlights are from the same document and page
            first_highlight = highlights[0]
            if not all(h.document_path == first_highlight.document_path and 
                      h.page_number == first_highlight.page_number for h in highlights):
                logger.error("Cannot merge highlights from different documents or pages")
                return None
            
            # Calculate merged selection bounds
            min_start = min(h.text_selection.start_char_index for h in highlights)
            max_end = max(h.text_selection.end_char_index for h in highlights)
            
            # Find the highlight with the earliest start position for positioning
            start_highlight = min(highlights, key=lambda h: h.text_selection.start_char_index)
            end_highlight = max(highlights, key=lambda h: h.text_selection.end_char_index)
            
            # Create merged text selection
            merged_selection = TextSelection(
                start_position=start_highlight.text_selection.start_position,
                end_position=end_highlight.text_selection.end_position,
                start_char_index=min_start,
                end_char_index=max_end,
                selected_text=" ".join(h.highlighted_text for h in highlights)
            )
            
            # Combine notes
            combined_notes = " | ".join(h.note for h in highlights if h.note.strip())
            
            # Use provided color or the color of the first highlight
            merge_color = new_color or first_highlight.color
            
            # Create merged highlight
            merged_highlight = self.create_highlight(
                document_path=first_highlight.document_path,
                page_number=first_highlight.page_number,
                text_selection=merged_selection,
                color=merge_color,
                note=combined_notes,
                category=first_highlight.category
            )
            
            if merged_highlight:
                # Delete original highlights
                for highlight_id in highlight_ids:
                    self.delete_highlight(highlight_id)
                
                logger.info(f"Merged {len(highlight_ids)} highlights into {merged_highlight.id}")
                return merged_highlight
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to merge highlights: {e}")
            return None
    
    def split_highlight(self, highlight_id: str, split_position: int) -> Optional[List[Highlight]]:
        """Split a highlight at the specified character position"""
        highlight = self.get_highlight_by_id(highlight_id)
        if not highlight:
            return None
        
        try:
            # Validate split position
            if (split_position <= highlight.text_selection.start_char_index or 
                split_position >= highlight.text_selection.end_char_index):
                logger.error("Invalid split position")
                return None
            
            # Create first part
            first_selection = TextSelection(
                start_position=highlight.text_selection.start_position,
                end_position=Point(0, 0),  # Will need to be calculated based on split
                start_char_index=highlight.text_selection.start_char_index,
                end_char_index=split_position,
                selected_text=highlight.highlighted_text[:split_position - highlight.text_selection.start_char_index]
            )
            
            # Create second part
            second_selection = TextSelection(
                start_position=Point(0, 0),  # Will need to be calculated based on split
                end_position=highlight.text_selection.end_position,
                start_char_index=split_position,
                end_char_index=highlight.text_selection.end_char_index,
                selected_text=highlight.highlighted_text[split_position - highlight.text_selection.start_char_index:]
            )
            
            # Create new highlights
            first_highlight = self.create_highlight(
                document_path=highlight.document_path,
                page_number=highlight.page_number,
                text_selection=first_selection,
                color=highlight.color,
                note=highlight.note,
                category=highlight.category
            )
            
            second_highlight = self.create_highlight(
                document_path=highlight.document_path,
                page_number=highlight.page_number,
                text_selection=second_selection,
                color=highlight.color,
                note=highlight.note,
                category=highlight.category
            )
            
            if first_highlight and second_highlight:
                # Delete original highlight
                self.delete_highlight(highlight_id)
                logger.info(f"Split highlight {highlight_id} into two parts")
                return [first_highlight, second_highlight]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to split highlight: {e}")
            return None
    
    def get_highlight_statistics(self, document_path: str) -> Dict:
        """Get statistics about highlights for a document"""
        highlights = self.get_highlights(document_path)
        
        if not highlights:
            return {
                'total_count': 0,
                'by_color': {},
                'by_category': {},
                'with_notes': 0,
                'pages_with_highlights': [],
                'total_highlighted_text': 0
            }
        
        # Count by color
        color_counts = {}
        for highlight in highlights:
            color_counts[highlight.color] = color_counts.get(highlight.color, 0) + 1
        
        # Count by category
        category_counts = {}
        for highlight in highlights:
            category_counts[highlight.category] = category_counts.get(highlight.category, 0) + 1
        
        # Count highlights with notes
        with_notes = sum(1 for h in highlights if h.note.strip())
        
        # Get pages with highlights
        pages_with_highlights = sorted(list(set(h.page_number for h in highlights)))
        
        # Calculate total highlighted text length
        total_text_length = sum(len(h.highlighted_text) for h in highlights)
        
        return {
            'total_count': len(highlights),
            'by_color': color_counts,
            'by_category': category_counts,
            'with_notes': with_notes,
            'pages_with_highlights': pages_with_highlights,
            'total_highlighted_text': total_text_length
        }
    
    def export_highlights(self, document_path: str, include_notes: bool = True) -> List[dict]:
        """Export highlights as a list of dictionaries"""
        highlights = self.get_highlights(document_path)
        exported = []
        
        for highlight in highlights:
            data = highlight.to_dict()
            if not include_notes:
                data.pop('note', None)
            exported.append(data)
        
        return exported
    
    def import_highlights(self, document_path: str, highlight_data: List[dict]) -> int:
        """Import highlights from a list of dictionaries"""
        imported_count = 0
        
        for data in highlight_data:
            try:
                # Ensure document path matches
                data['document_path'] = document_path
                
                highlight = Highlight.from_dict(data)
                if self.storage.save_annotation(highlight):
                    imported_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to import highlight: {e}")
                continue
        
        logger.info(f"Imported {imported_count} highlights for {document_path}")
        return imported_count
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if a color is valid"""
        # Check if it's a predefined color
        predefined_colors = [c.value for c in HighlightColor]
        if color in predefined_colors:
            return True
        
        # Check if it's a valid hex color
        if color.startswith('#') and len(color) == 7:
            try:
                int(color[1:], 16)
                return True
            except ValueError:
                pass
        
        return False
    
    def _selections_overlap(self, selection1: TextSelection, selection2: TextSelection) -> bool:
        """Check if two text selections overlap"""
        return not (selection1.end_char_index <= selection2.start_char_index or 
                   selection2.end_char_index <= selection1.start_char_index)