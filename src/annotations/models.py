"""
Data Models for Annotation System
Defines all annotation types and supporting data structures
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
import uuid
import json

class AnnotationType(Enum):
    """Enumeration of annotation types"""
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"
    NOTE = "note"

class HighlightColor(Enum):
    """Predefined highlight colors"""
    YELLOW = "#FFFF00"
    GREEN = "#00FF00"
    BLUE = "#0080FF"
    PINK = "#FF69B4"
    ORANGE = "#FFA500"
    PURPLE = "#8A2BE2"
    RED = "#FF0000"
    CYAN = "#00FFFF"

@dataclass
class Point:
    """Represents a 2D point for positioning"""
    x: float
    y: float
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Point':
        return cls(x=data["x"], y=data["y"])

@dataclass
class TextSelection:
    """Represents a text selection with precise positioning"""
    start_position: Point
    end_position: Point
    start_char_index: int
    end_char_index: int
    selected_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_position": self.start_position.to_dict(),
            "end_position": self.end_position.to_dict(),
            "start_char_index": self.start_char_index,
            "end_char_index": self.end_char_index,
            "selected_text": self.selected_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextSelection':
        return cls(
            start_position=Point.from_dict(data["start_position"]),
            end_position=Point.from_dict(data["end_position"]),
            start_char_index=data["start_char_index"],
            end_char_index=data["end_char_index"],
            selected_text=data.get("selected_text", "")
        )

@dataclass
class Annotation(ABC):
    """Base class for all annotation types"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_path: str = ""
    page_number: int = 1
    category: str = "default"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Ensure updated_at is set"""
        if self.updated_at == self.created_at:
            self.updated_at = datetime.now()
    
    @abstractmethod
    def get_type(self) -> AnnotationType:
        """Return the annotation type"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert annotation to dictionary for storage"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        """Create annotation from dictionary"""
        pass
    
    @abstractmethod
    def get_display_text(self) -> str:
        """Get text for display in UI"""
        pass
    
    @abstractmethod
    def get_search_text(self) -> str:
        """Get text for search indexing"""
        pass
    
    def update_timestamp(self):
        """Update the modification timestamp"""
        self.updated_at = datetime.now()

@dataclass
class Bookmark(Annotation):
    """Bookmark annotation for marking important pages"""
    title: str = ""
    description: str = ""
    position: Optional[Point] = None
    
    def get_type(self) -> AnnotationType:
        return AnnotationType.BOOKMARK
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = {
            "id": self.id,
            "document_path": self.document_path,
            "page_number": self.page_number,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "title": self.title,
            "description": self.description
        }
        
        if self.position:
            base_dict["position"] = self.position.to_dict()
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bookmark':
        position = None
        if "position" in data and data["position"]:
            position = Point.from_dict(data["position"])
        
        return cls(
            id=data["id"],
            document_path=data["document_path"],
            page_number=data["page_number"],
            category=data.get("category", "default"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            title=data.get("title", ""),
            description=data.get("description", ""),
            position=position
        )
    
    def get_display_text(self) -> str:
        if self.title:
            return self.title
        return f"Bookmark - Page {self.page_number}"
    
    def get_search_text(self) -> str:
        return f"{self.title} {self.description}".strip()

@dataclass
class Highlight(Annotation):
    """Text highlight annotation with color coding"""
    text_selection: TextSelection = field(default_factory=lambda: TextSelection(
        Point(0, 0), Point(0, 0), 0, 0
    ))
    highlighted_text: str = ""
    color: str = HighlightColor.YELLOW.value
    note: str = ""  # Optional note attached to highlight
    
    def get_type(self) -> AnnotationType:
        return AnnotationType.HIGHLIGHT
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "document_path": self.document_path,
            "page_number": self.page_number,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "text_selection": self.text_selection.to_dict(),
            "highlighted_text": self.highlighted_text,
            "color": self.color,
            "note": self.note
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Highlight':
        return cls(
            id=data["id"],
            document_path=data["document_path"],
            page_number=data["page_number"],
            category=data.get("category", "default"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            text_selection=TextSelection.from_dict(data["text_selection"]),
            highlighted_text=data.get("highlighted_text", ""),
            color=data.get("color", HighlightColor.YELLOW.value),
            note=data.get("note", "")
        )
    
    def get_display_text(self) -> str:
        text = self.highlighted_text[:50]
        if len(self.highlighted_text) > 50:
            text += "..."
        return f'"{text}"'
    
    def get_search_text(self) -> str:
        return f"{self.highlighted_text} {self.note}".strip()

@dataclass
class Note(Annotation):
    """Note annotation for detailed comments"""
    position: Point = field(default_factory=lambda: Point(0, 0))
    content: str = ""  # Rich text HTML content
    plain_text: str = ""  # Plain text for searching
    parent_note_id: Optional[str] = None  # For threaded notes
    
    def get_type(self) -> AnnotationType:
        return AnnotationType.NOTE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "document_path": self.document_path,
            "page_number": self.page_number,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "position": self.position.to_dict(),
            "content": self.content,
            "plain_text": self.plain_text,
            "parent_note_id": self.parent_note_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        return cls(
            id=data["id"],
            document_path=data["document_path"],
            page_number=data["page_number"],
            category=data.get("category", "default"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            position=Point.from_dict(data["position"]),
            content=data.get("content", ""),
            plain_text=data.get("plain_text", ""),
            parent_note_id=data.get("parent_note_id")
        )
    
    def get_display_text(self) -> str:
        text = self.plain_text or self.content
        if len(text) > 50:
            text = text[:50] + "..."
        return text or "Empty Note"
    
    def get_search_text(self) -> str:
        return self.plain_text or self.content

@dataclass
class AnnotationCategory:
    """Category for organizing annotations"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    color: str = "#808080"  # Default gray
    description: str = ""
    annotation_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "annotation_count": self.annotation_count,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotationCategory':
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color", "#808080"),
            description=data.get("description", ""),
            annotation_count=data.get("annotation_count", 0),
            created_at=datetime.fromisoformat(data["created_at"])
        )

@dataclass
class AnnotationFilter:
    """Filter criteria for annotation searches"""
    document_path: Optional[str] = None
    annotation_type: Optional[AnnotationType] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page_range: Optional[Tuple[int, int]] = None
    search_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.document_path:
            result["document_path"] = self.document_path
        if self.annotation_type:
            result["annotation_type"] = self.annotation_type.value
        if self.category:
            result["category"] = self.category
        if self.date_from:
            result["date_from"] = self.date_from.isoformat()
        if self.date_to:
            result["date_to"] = self.date_to.isoformat()
        if self.page_range:
            result["page_range"] = list(self.page_range)
        if self.search_text:
            result["search_text"] = self.search_text
        return result

@dataclass
class AnnotationSearchResult:
    """Search result containing annotation and relevance information"""
    annotation: Annotation
    relevance_score: float
    context_snippet: str
    match_highlights: List[Tuple[int, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "annotation": self.annotation.to_dict(),
            "annotation_type": self.annotation.get_type().value,
            "relevance_score": self.relevance_score,
            "context_snippet": self.context_snippet,
            "match_highlights": self.match_highlights
        }

# Default categories
DEFAULT_CATEGORIES = [
    AnnotationCategory(name="Important", color="#FF0000", description="Important content"),
    AnnotationCategory(name="To Review", color="#FFA500", description="Content to review later"),
    AnnotationCategory(name="Questions", color="#0080FF", description="Questions and clarifications"),
    AnnotationCategory(name="Ideas", color="#00FF00", description="Ideas and insights"),
    AnnotationCategory(name="References", color="#8A2BE2", description="References and citations"),
]