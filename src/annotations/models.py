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
    """Category for organizing annotations with hierarchical support"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    color: str = "#808080"  # Default gray
    description: str = ""
    parent_id: Optional[str] = None  # For hierarchical categories
    sort_order: int = 0  # For custom ordering
    is_default: bool = False  # System default categories
    is_active: bool = True  # Soft delete support
    annotation_count: int = 0  # Cached count for performance
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extensible metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Ensure updated_at is set and validate data"""
        if self.updated_at == self.created_at:
            self.updated_at = datetime.now()
        
        # Validate color format
        if not self.color.startswith('#') or len(self.color) != 7:
            self.color = "#808080"
        
        # Validate name
        if not self.name.strip():
            raise ValueError("Category name cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "annotation_count": self.annotation_count,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotationCategory':
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color", "#808080"),
            description=data.get("description", ""),
            parent_id=data.get("parent_id"),
            sort_order=data.get("sort_order", 0),
            is_default=data.get("is_default", False),
            is_active=data.get("is_active", True),
            annotation_count=data.get("annotation_count", 0),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def update_timestamp(self):
        """Update the modification timestamp"""
        self.updated_at = datetime.now()
    
    def is_child_of(self, parent_category: 'AnnotationCategory') -> bool:
        """Check if this category is a child of the given parent"""
        return self.parent_id == parent_category.id
    
    def get_full_path(self, categories: List['AnnotationCategory']) -> str:
        """Get the full hierarchical path of this category"""
        if not self.parent_id:
            return self.name
        
        # Find parent category
        parent = next((cat for cat in categories if cat.id == self.parent_id), None)
        if parent:
            return f"{parent.get_full_path(categories)} > {self.name}"
        return self.name
    
    def validate_hierarchy(self, categories: List['AnnotationCategory']) -> bool:
        """Validate that this category doesn't create circular references"""
        if not self.parent_id:
            return True
        
        visited = set()
        current_id = self.parent_id
        
        while current_id:
            if current_id == self.id:
                return False  # Circular reference
            
            if current_id in visited:
                return False  # Circular reference
            
            visited.add(current_id)
            parent = next((cat for cat in categories if cat.id == current_id), None)
            if not parent:
                break
            current_id = parent.parent_id
        
        return True

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

@dataclass
class CategoryAssignment:
    """Represents the assignment of a category to an annotation"""
    annotation_id: str
    category_id: str
    assigned_at: datetime = field(default_factory=datetime.now)
    assigned_by: str = "system"  # User identifier or system
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "annotation_id": self.annotation_id,
            "category_id": self.category_id,
            "assigned_at": self.assigned_at.isoformat(),
            "assigned_by": self.assigned_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategoryAssignment':
        return cls(
            annotation_id=data["annotation_id"],
            category_id=data["category_id"],
            assigned_at=datetime.fromisoformat(data["assigned_at"]),
            assigned_by=data.get("assigned_by", "system")
        )

@dataclass
class SearchPreset:
    """Saved search filter configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    filters: Dict[str, Any] = field(default_factory=dict)
    is_public: bool = False  # Can be shared with other users
    usage_count: int = 0  # Track how often it's used
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "filters": self.filters,
            "is_public": self.is_public,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchPreset':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            filters=data.get("filters", {}),
            is_public=data.get("is_public", False),
            usage_count=data.get("usage_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def update_timestamp(self):
        """Update the modification timestamp"""
        self.updated_at = datetime.now()
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.update_timestamp()

@dataclass
class BulkOperation:
    """Represents a bulk operation on annotations"""
    operation_type: str  # "categorize", "delete", "export", "move"
    annotation_ids: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_type": self.operation_type,
            "annotation_ids": self.annotation_ids,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class BulkOperationResult:
    """Result of a bulk operation"""
    operation: BulkOperation
    success_count: int = 0
    failure_count: int = 0
    errors: List[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation.to_dict(),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "errors": self.errors,
            "completed_at": self.completed_at.isoformat()
        }
    
    @property
    def total_count(self) -> int:
        return self.success_count + self.failure_count
    
    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count

@dataclass
class AnnotationStatistics:
    """Statistics about annotations"""
    total_annotations: int = 0
    bookmarks_count: int = 0
    highlights_count: int = 0
    notes_count: int = 0
    categories_count: int = 0
    documents_count: int = 0
    most_used_category: Optional[str] = None
    most_annotated_document: Optional[str] = None
    annotations_by_date: Dict[str, int] = field(default_factory=dict)  # Date -> count
    annotations_by_category: Dict[str, int] = field(default_factory=dict)  # Category -> count
    annotations_by_type: Dict[str, int] = field(default_factory=dict)  # Type -> count
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_annotations": self.total_annotations,
            "bookmarks_count": self.bookmarks_count,
            "highlights_count": self.highlights_count,
            "notes_count": self.notes_count,
            "categories_count": self.categories_count,
            "documents_count": self.documents_count,
            "most_used_category": self.most_used_category,
            "most_annotated_document": self.most_annotated_document,
            "annotations_by_date": self.annotations_by_date,
            "annotations_by_category": self.annotations_by_category,
            "annotations_by_type": self.annotations_by_type
        }

# Enhanced default categories with hierarchy
DEFAULT_CATEGORIES = [
    # Root categories
    AnnotationCategory(
        name="Important", 
        color="#FF4444", 
        description="Critical and important content",
        is_default=True,
        sort_order=1
    ),
    AnnotationCategory(
        name="Research", 
        color="#4444FF", 
        description="Research-related annotations",
        is_default=True,
        sort_order=2
    ),
    AnnotationCategory(
        name="Personal", 
        color="#44FF44", 
        description="Personal thoughts and ideas",
        is_default=True,
        sort_order=3
    ),
    AnnotationCategory(
        name="Questions", 
        color="#FF8844", 
        description="Questions and clarifications needed",
        is_default=True,
        sort_order=4
    ),
    AnnotationCategory(
        name="References", 
        color="#8844FF", 
        description="References and citations",
        is_default=True,
        sort_order=5
    ),
]

# Category templates for quick setup
CATEGORY_TEMPLATES = {
    "academic": [
        {"name": "Literature Review", "color": "#3498db", "description": "Literature review notes"},
        {"name": "Methodology", "color": "#e74c3c", "description": "Methodology and methods"},
        {"name": "Results", "color": "#2ecc71", "description": "Results and findings"},
        {"name": "Discussion", "color": "#f39c12", "description": "Discussion and analysis"},
        {"name": "Future Work", "color": "#9b59b6", "description": "Future research directions"},
    ],
    "business": [
        {"name": "Strategy", "color": "#34495e", "description": "Strategic insights"},
        {"name": "Market Analysis", "color": "#16a085", "description": "Market research and analysis"},
        {"name": "Competitive Intelligence", "color": "#e67e22", "description": "Competitor information"},
        {"name": "Action Items", "color": "#c0392b", "description": "Tasks and action items"},
        {"name": "Key Metrics", "color": "#8e44ad", "description": "Important metrics and KPIs"},
    ],
    "learning": [
        {"name": "Key Concepts", "color": "#2980b9", "description": "Important concepts to remember"},
        {"name": "Examples", "color": "#27ae60", "description": "Examples and case studies"},
        {"name": "Practice", "color": "#f1c40f", "description": "Practice problems and exercises"},
        {"name": "Review", "color": "#e74c3c", "description": "Content to review later"},
        {"name": "Mastered", "color": "#95a5a6", "description": "Fully understood content"},
    ]
}