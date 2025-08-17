"""
Annotation Storage Layer
Handles persistent storage and retrieval of all annotation types
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager

from .models import (
    Annotation, Bookmark, Highlight, Note, AnnotationCategory,
    AnnotationType, AnnotationFilter, AnnotationSearchResult,
    CategoryAssignment, SearchPreset, BulkOperation, BulkOperationResult,
    AnnotationStatistics, DEFAULT_CATEGORIES
)

logger = logging.getLogger("ebook_reader")

class AnnotationStorage:
    """Handles all annotation storage operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize storage with database path"""
        if db_path is None:
            db_path = str(Path.home() / '.ebook_reader' / 'annotations.db')
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the annotation database with required tables"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with self.get_connection() as conn:
            # Main annotations table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS annotations (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    document_path TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    data JSON NOT NULL,
                    category TEXT DEFAULT 'default',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Enhanced categories table with hierarchy support
            conn.execute('''
                CREATE TABLE IF NOT EXISTS annotation_categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL,
                    description TEXT,
                    parent_id TEXT REFERENCES annotation_categories(id),
                    sort_order INTEGER DEFAULT 0,
                    is_default BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    annotation_count INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, parent_id)
                )
            ''')
            
            # Category assignments table for many-to-many relationships
            conn.execute('''
                CREATE TABLE IF NOT EXISTS annotation_category_assignments (
                    annotation_id TEXT REFERENCES annotations(id) ON DELETE CASCADE,
                    category_id TEXT REFERENCES annotation_categories(id) ON DELETE CASCADE,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_by TEXT DEFAULT 'system',
                    PRIMARY KEY (annotation_id, category_id)
                )
            ''')
            
            # Search presets table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS search_presets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    filters TEXT NOT NULL,
                    is_public BOOLEAN DEFAULT FALSE,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_annotations_document ON annotations(document_path)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_annotations_page ON annotations(document_path, page_number)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_annotations_type ON annotations(type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_annotations_category ON annotations(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_annotations_created ON annotations(created_at)')
            
            # Category indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_categories_parent ON annotation_categories(parent_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_categories_name ON annotation_categories(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_categories_active ON annotation_categories(is_active)')
            
            # Category assignment indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_assignments_annotation ON annotation_category_assignments(annotation_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_assignments_category ON annotation_category_assignments(category_id)')
            
            # Search preset indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_presets_name ON search_presets(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_presets_usage ON search_presets(usage_count DESC)')
            
            # Full-text search table
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS annotation_search USING fts5(
                    annotation_id,
                    content
                )
            ''')
            
            # Initialize default categories if none exist
            cursor = conn.execute('SELECT COUNT(*) FROM annotation_categories')
            if cursor.fetchone()[0] == 0:
                self._create_default_categories(conn)
            
            conn.commit()
    
    def _create_default_categories(self, conn: sqlite3.Connection):
        """Create default annotation categories with enhanced schema"""
        for category in DEFAULT_CATEGORIES:
            conn.execute('''
                INSERT INTO annotation_categories 
                (id, name, color, description, parent_id, sort_order, is_default, 
                 is_active, annotation_count, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category.id, category.name, category.color, category.description,
                category.parent_id, category.sort_order, category.is_default,
                category.is_active, category.annotation_count, 
                json.dumps(category.metadata),
                category.created_at.isoformat(), category.updated_at.isoformat()
            ))
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_annotation(self, annotation: Annotation) -> bool:
        """Save an annotation to the database"""
        try:
            with self.get_connection() as conn:
                # Update timestamp
                annotation.update_timestamp()
                
                # Convert annotation to storage format
                data = annotation.to_dict()
                
                # Insert or update annotation
                conn.execute('''
                    INSERT OR REPLACE INTO annotations 
                    (id, type, document_path, page_number, data, category, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    annotation.id,
                    annotation.get_type().value,
                    annotation.document_path,
                    annotation.page_number,
                    json.dumps(data),
                    annotation.category,
                    annotation.created_at.isoformat(),
                    annotation.updated_at.isoformat()
                ))
                
                # Update search index
                search_text = annotation.get_search_text()
                if search_text.strip():
                    conn.execute('''
                        INSERT OR REPLACE INTO annotation_search (annotation_id, content)
                        VALUES (?, ?)
                    ''', (annotation.id, search_text))
                
                # Update category count
                self._update_category_count(conn, annotation.category)
                
                conn.commit()
                logger.debug(f"Saved annotation: {annotation.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save annotation {annotation.id}: {e}")
            return False
    
    def load_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """Load a single annotation by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT type, data FROM annotations WHERE id = ?
                ''', (annotation_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                annotation_type = AnnotationType(row['type'])
                data = json.loads(row['data'])
                
                return self._create_annotation_from_data(annotation_type, data)
                
        except Exception as e:
            logger.error(f"Failed to load annotation {annotation_id}: {e}")
            return None
    
    def load_annotations(self, document_path: str, page_number: Optional[int] = None,
                        annotation_type: Optional[AnnotationType] = None) -> List[Annotation]:
        """Load annotations for a document or specific page"""
        try:
            with self.get_connection() as conn:
                query = 'SELECT type, data FROM annotations WHERE document_path = ?'
                params = [document_path]
                
                if page_number is not None:
                    query += ' AND page_number = ?'
                    params.append(page_number)
                
                if annotation_type is not None:
                    query += ' AND type = ?'
                    params.append(annotation_type.value)
                
                query += ' ORDER BY page_number, created_at'
                
                cursor = conn.execute(query, params)
                annotations = []
                
                for row in cursor.fetchall():
                    try:
                        ann_type = AnnotationType(row['type'])
                        data = json.loads(row['data'])
                        annotation = self._create_annotation_from_data(ann_type, data)
                        if annotation:
                            annotations.append(annotation)
                    except Exception as e:
                        logger.warning(f"Failed to load annotation from row: {e}")
                        continue
                
                return annotations
                
        except Exception as e:
            logger.error(f"Failed to load annotations for {document_path}: {e}")
            return []
    
    def delete_annotation(self, annotation_id: str) -> bool:
        """Delete an annotation"""
        try:
            with self.get_connection() as conn:
                # Get annotation info before deletion for category count update
                cursor = conn.execute('SELECT category FROM annotations WHERE id = ?', (annotation_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False
                
                category = row['category']
                
                # Delete annotation
                conn.execute('DELETE FROM annotations WHERE id = ?', (annotation_id,))
                
                # Delete from search index
                conn.execute('DELETE FROM annotation_search WHERE annotation_id = ?', (annotation_id,))
                
                # Update category count
                self._update_category_count(conn, category)
                
                conn.commit()
                logger.debug(f"Deleted annotation: {annotation_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete annotation {annotation_id}: {e}")
            return False
    
    def search_annotations(self, query: str, filters: Optional[AnnotationFilter] = None,
                          limit: int = 100) -> List[AnnotationSearchResult]:
        """Search annotations with optional filters"""
        try:
            with self.get_connection() as conn:
                # Build search query
                if query.strip():
                    # Use FTS search
                    search_query = '''
                        SELECT a.type, a.data, 1.0 as relevance
                        FROM annotation_search s
                        JOIN annotations a ON s.annotation_id = a.id
                        WHERE s.content MATCH ?
                    '''
                    params = [query]
                else:
                    # No text search, just filter
                    search_query = '''
                        SELECT type, data, 1.0 as relevance
                        FROM annotations
                        WHERE 1=1
                    '''
                    params = []
                
                # Apply filters
                if filters:
                    if filters.document_path:
                        search_query += ' AND a.document_path = ?' if query.strip() else ' AND document_path = ?'
                        params.append(filters.document_path)
                    
                    if filters.annotation_type:
                        search_query += ' AND a.type = ?' if query.strip() else ' AND type = ?'
                        params.append(filters.annotation_type.value)
                    
                    if filters.category:
                        search_query += ' AND a.category = ?' if query.strip() else ' AND category = ?'
                        params.append(filters.category)
                    
                    if filters.date_from:
                        search_query += ' AND a.created_at >= ?' if query.strip() else ' AND created_at >= ?'
                        params.append(filters.date_from.isoformat())
                    
                    if filters.date_to:
                        search_query += ' AND a.created_at <= ?' if query.strip() else ' AND created_at <= ?'
                        params.append(filters.date_to.isoformat())
                    
                    if filters.page_range:
                        search_query += ' AND a.page_number BETWEEN ? AND ?' if query.strip() else ' AND page_number BETWEEN ? AND ?'
                        params.extend(filters.page_range)
                
                search_query += ' ORDER BY relevance DESC LIMIT ?'
                params.append(limit)
                
                cursor = conn.execute(search_query, params)
                results = []
                
                for row in cursor.fetchall():
                    try:
                        ann_type = AnnotationType(row['type'])
                        data = json.loads(row['data'])
                        annotation = self._create_annotation_from_data(ann_type, data)
                        
                        if annotation:
                            # Create search result
                            context = self._extract_context(annotation, query)
                            result = AnnotationSearchResult(
                                annotation=annotation,
                                relevance_score=abs(float(row['relevance'])),
                                context_snippet=context,
                                match_highlights=[]  # TODO: Implement highlight extraction
                            )
                            results.append(result)
                    except Exception as e:
                        logger.warning(f"Failed to process search result: {e}")
                        continue
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to search annotations: {e}")
            return []
    
    def get_categories(self, include_inactive: bool = False) -> List[AnnotationCategory]:
        """Get all annotation categories with hierarchy support"""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT id, name, color, description, parent_id, sort_order,
                           is_default, is_active, annotation_count, metadata,
                           created_at, updated_at
                    FROM annotation_categories
                '''
                
                if not include_inactive:
                    query += ' WHERE is_active = TRUE'
                
                query += ' ORDER BY sort_order, name'
                
                cursor = conn.execute(query)
                categories = []
                
                for row in cursor.fetchall():
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    category = AnnotationCategory(
                        id=row['id'],
                        name=row['name'],
                        color=row['color'],
                        description=row['description'] or "",
                        parent_id=row['parent_id'],
                        sort_order=row['sort_order'],
                        is_default=bool(row['is_default']),
                        is_active=bool(row['is_active']),
                        annotation_count=row['annotation_count'],
                        metadata=metadata,
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at'])
                    )
                    categories.append(category)
                
                return categories
                
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    def get_category_by_id(self, category_id: str) -> Optional[AnnotationCategory]:
        """Get a specific category by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, name, color, description, parent_id, sort_order,
                           is_default, is_active, annotation_count, metadata,
                           created_at, updated_at
                    FROM annotation_categories
                    WHERE id = ?
                ''', (category_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                return AnnotationCategory(
                    id=row['id'],
                    name=row['name'],
                    color=row['color'],
                    description=row['description'] or "",
                    parent_id=row['parent_id'],
                    sort_order=row['sort_order'],
                    is_default=bool(row['is_default']),
                    is_active=bool(row['is_active']),
                    annotation_count=row['annotation_count'],
                    metadata=metadata,
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                
        except Exception as e:
            logger.error(f"Failed to get category {category_id}: {e}")
            return None
    
    def save_category(self, category: AnnotationCategory) -> bool:
        """Save an annotation category with full hierarchy support"""
        try:
            with self.get_connection() as conn:
                # Update timestamp
                category.update_timestamp()
                
                conn.execute('''
                    INSERT OR REPLACE INTO annotation_categories
                    (id, name, color, description, parent_id, sort_order,
                     is_default, is_active, annotation_count, metadata,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    category.id, category.name, category.color,
                    category.description, category.parent_id, category.sort_order,
                    category.is_default, category.is_active, category.annotation_count,
                    json.dumps(category.metadata),
                    category.created_at.isoformat(), category.updated_at.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to save category {category.name}: {e}")
            return False
    
    def delete_category(self, category_id: str, reassign_to: Optional[str] = None) -> bool:
        """Delete a category with optional reassignment"""
        try:
            with self.get_connection() as conn:
                # Check if category has children
                cursor = conn.execute('''
                    SELECT COUNT(*) as count FROM annotation_categories WHERE parent_id = ?
                ''', (category_id,))
                
                if cursor.fetchone()['count'] > 0:
                    # Move children to parent or root level
                    parent_cursor = conn.execute('''
                        SELECT parent_id FROM annotation_categories WHERE id = ?
                    ''', (category_id,))
                    parent_row = parent_cursor.fetchone()
                    new_parent = parent_row['parent_id'] if parent_row else None
                    
                    conn.execute('''
                        UPDATE annotation_categories SET parent_id = ? WHERE parent_id = ?
                    ''', (new_parent, category_id))
                
                # Reassign or remove category assignments
                if reassign_to:
                    conn.execute('''
                        UPDATE annotation_category_assignments 
                        SET category_id = ? WHERE category_id = ?
                    ''', (reassign_to, category_id))
                else:
                    conn.execute('''
                        DELETE FROM annotation_category_assignments WHERE category_id = ?
                    ''', (category_id,))
                
                # Update legacy category field in annotations table
                reassign_category = reassign_to or 'default'
                conn.execute('''
                    UPDATE annotations SET category = ? WHERE category = ?
                ''', (reassign_category, category_id))
                
                # Delete category
                conn.execute('DELETE FROM annotation_categories WHERE id = ?', (category_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete category {category_id}: {e}")
            return False
    
    def assign_category(self, annotation_id: str, category_id: str, assigned_by: str = "system") -> bool:
        """Assign a category to an annotation"""
        try:
            with self.get_connection() as conn:
                # Insert category assignment
                conn.execute('''
                    INSERT OR REPLACE INTO annotation_category_assignments
                    (annotation_id, category_id, assigned_at, assigned_by)
                    VALUES (?, ?, ?, ?)
                ''', (annotation_id, category_id, datetime.now().isoformat(), assigned_by))
                
                # Update legacy category field for backward compatibility
                conn.execute('''
                    UPDATE annotations SET category = ? WHERE id = ?
                ''', (category_id, annotation_id))
                
                # Update category count
                self._update_category_count(conn, category_id)
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to assign category {category_id} to annotation {annotation_id}: {e}")
            return False
    
    def remove_category_assignment(self, annotation_id: str, category_id: str) -> bool:
        """Remove a category assignment from an annotation"""
        try:
            with self.get_connection() as conn:
                # Remove category assignment
                conn.execute('''
                    DELETE FROM annotation_category_assignments
                    WHERE annotation_id = ? AND category_id = ?
                ''', (annotation_id, category_id))
                
                # Check if annotation has other categories
                cursor = conn.execute('''
                    SELECT COUNT(*) as count FROM annotation_category_assignments
                    WHERE annotation_id = ?
                ''', (annotation_id,))
                
                if cursor.fetchone()['count'] == 0:
                    # No categories left, set to default
                    conn.execute('''
                        UPDATE annotations SET category = 'default' WHERE id = ?
                    ''', (annotation_id,))
                
                # Update category count
                self._update_category_count(conn, category_id)
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove category assignment: {e}")
            return False
    
    def get_annotation_categories(self, annotation_id: str) -> List[AnnotationCategory]:
        """Get all categories assigned to an annotation"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT c.id, c.name, c.color, c.description, c.parent_id,
                           c.sort_order, c.is_default, c.is_active, c.annotation_count,
                           c.metadata, c.created_at, c.updated_at
                    FROM annotation_categories c
                    JOIN annotation_category_assignments a ON c.id = a.category_id
                    WHERE a.annotation_id = ?
                    ORDER BY c.sort_order, c.name
                ''', (annotation_id,))
                
                categories = []
                for row in cursor.fetchall():
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    category = AnnotationCategory(
                        id=row['id'],
                        name=row['name'],
                        color=row['color'],
                        description=row['description'] or "",
                        parent_id=row['parent_id'],
                        sort_order=row['sort_order'],
                        is_default=bool(row['is_default']),
                        is_active=bool(row['is_active']),
                        annotation_count=row['annotation_count'],
                        metadata=metadata,
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at'])
                    )
                    categories.append(category)
                
                return categories
                
        except Exception as e:
            logger.error(f"Failed to get categories for annotation {annotation_id}: {e}")
            return []
    
    def get_annotation_stats(self, document_path: Optional[str] = None) -> Dict[str, Any]:
        """Get annotation statistics"""
        try:
            with self.get_connection() as conn:
                base_query = 'SELECT type, COUNT(*) as count FROM annotations'
                params = []
                
                if document_path:
                    base_query += ' WHERE document_path = ?'
                    params.append(document_path)
                
                base_query += ' GROUP BY type'
                
                cursor = conn.execute(base_query, params)
                type_counts = {row['type']: row['count'] for row in cursor.fetchall()}
                
                # Get total count
                total_query = 'SELECT COUNT(*) as total FROM annotations'
                if document_path:
                    total_query += ' WHERE document_path = ?'
                
                cursor = conn.execute(total_query, params)
                total_count = cursor.fetchone()['total']
                
                return {
                    'total': total_count,
                    'by_type': type_counts,
                    'document_path': document_path
                }
                
        except Exception as e:
            logger.error(f"Failed to get annotation stats: {e}")
            return {'total': 0, 'by_type': {}, 'document_path': document_path}
    
    def _create_annotation_from_data(self, annotation_type: AnnotationType, data: Dict[str, Any]) -> Optional[Annotation]:
        """Create annotation object from stored data"""
        try:
            if annotation_type == AnnotationType.BOOKMARK:
                return Bookmark.from_dict(data)
            elif annotation_type == AnnotationType.HIGHLIGHT:
                return Highlight.from_dict(data)
            elif annotation_type == AnnotationType.NOTE:
                return Note.from_dict(data)
            else:
                logger.warning(f"Unknown annotation type: {annotation_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to create annotation from data: {e}")
            return None
    
    def _update_category_count(self, conn: sqlite3.Connection, category: str):
        """Update annotation count for a category"""
        try:
            cursor = conn.execute('''
                SELECT COUNT(*) as count FROM annotations WHERE category = ?
            ''', (category,))
            
            count = cursor.fetchone()['count']
            
            conn.execute('''
                UPDATE annotation_categories SET annotation_count = ? WHERE id = ?
            ''', (count, category))
            
        except Exception as e:
            logger.warning(f"Failed to update category count for {category}: {e}")
    
    def _extract_context(self, annotation: Annotation, query: str) -> str:
        """Extract context snippet for search results"""
        search_text = annotation.get_search_text()
        display_text = annotation.get_display_text()
        
        if query and query.lower() in search_text.lower():
            # Find query in text and extract context
            query_pos = search_text.lower().find(query.lower())
            start = max(0, query_pos - 50)
            end = min(len(search_text), query_pos + len(query) + 50)
            context = search_text[start:end]
            
            if start > 0:
                context = "..." + context
            if end < len(search_text):
                context = context + "..."
            
            return context
        
        # Fallback to display text
        return display_text[:100] + ("..." if len(display_text) > 100 else "")
    
    def backup_annotations(self, backup_path: str) -> bool:
        """Create a backup of all annotations"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Annotations backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup annotations: {e}")
            return False
    
    def restore_annotations(self, backup_path: str) -> bool:
        """Restore annotations from backup"""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Annotations restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore annotations: {e}")
            return False
    
    # Search Preset Management
    def save_search_preset(self, preset) -> bool:
        """Save a search preset"""
        try:
            with self.get_connection() as conn:
                preset.update_timestamp()
                
                conn.execute('''
                    INSERT OR REPLACE INTO search_presets
                    (id, name, description, filters, is_public, usage_count,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    preset.id, preset.name, preset.description,
                    json.dumps(preset.filters), preset.is_public, preset.usage_count,
                    preset.created_at.isoformat(), preset.updated_at.isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to save search preset {preset.name}: {e}")
            return False
    
    def get_search_presets(self, include_public: bool = True):
        """Get all search presets"""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT id, name, description, filters, is_public, usage_count,
                           created_at, updated_at
                    FROM search_presets
                '''
                
                if not include_public:
                    query += ' WHERE is_public = FALSE'
                
                query += ' ORDER BY usage_count DESC, name'
                
                cursor = conn.execute(query)
                presets = []
                
                for row in cursor.fetchall():
                    from .models import SearchPreset
                    preset = SearchPreset(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'] or "",
                        filters=json.loads(row['filters']),
                        is_public=bool(row['is_public']),
                        usage_count=row['usage_count'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at'])
                    )
                    presets.append(preset)
                
                return presets
                
        except Exception as e:
            logger.error(f"Failed to get search presets: {e}")
            return []
    
    def delete_search_preset(self, preset_id: str) -> bool:
        """Delete a search preset"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM search_presets WHERE id = ?', (preset_id,))
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete search preset {preset_id}: {e}")
            return False
    
    def increment_preset_usage(self, preset_id: str) -> bool:
        """Increment usage count for a search preset"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE search_presets 
                    SET usage_count = usage_count + 1, updated_at = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), preset_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to increment preset usage {preset_id}: {e}")
            return False