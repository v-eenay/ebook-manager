"""
Category Manager
Handles category operations and hierarchy management
"""

import logging
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from .models import (
    AnnotationCategory, CategoryAssignment, SearchPreset,
    BulkOperation, BulkOperationResult, AnnotationStatistics,
    DEFAULT_CATEGORIES, CATEGORY_TEMPLATES
)
from .annotation_storage import AnnotationStorage

logger = logging.getLogger("ebook_reader")

class CategoryManager:
    """Manages annotation categories and their relationships"""
    
    def __init__(self, storage: AnnotationStorage):
        """Initialize category manager with storage"""
        self.storage = storage
        self._category_cache = {}
        self._hierarchy_cache = None
        self._cache_timestamp = None
    
    # Category CRUD Operations
    def create_category(self, name: str, color: str = "#808080", 
                       description: str = "", parent_id: Optional[str] = None,
                       sort_order: int = 0, is_active: bool = True) -> Optional[AnnotationCategory]:
        """Create a new category"""
        try:
            # Validate name uniqueness within parent
            if self._is_name_duplicate(name, parent_id):
                logger.error(f"Category name '{name}' already exists in this parent")
                return None
            
            # Create category
            category = AnnotationCategory(
                name=name.strip(),
                color=color,
                description=description.strip(),
                parent_id=parent_id,
                sort_order=sort_order,
                is_active=is_active
            )
            
            # Validate hierarchy
            categories = self.get_categories()
            if not category.validate_hierarchy(categories):
                logger.error(f"Category '{name}' would create circular reference")
                return None
            
            # Save to storage
            if self.storage.save_category(category):
                self._invalidate_cache()
                logger.info(f"Created category: {name}")
                return category
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create category '{name}': {e}")
            return None
    
    def update_category(self, category_id: str, **kwargs) -> bool:
        """Update an existing category"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.error(f"Category {category_id} not found")
                return False
            
            # Update fields
            if 'name' in kwargs:
                new_name = kwargs['name'].strip()
                if new_name != category.name:
                    if self._is_name_duplicate(new_name, category.parent_id, exclude_id=category_id):
                        logger.error(f"Category name '{new_name}' already exists")
                        return False
                    category.name = new_name
            
            if 'color' in kwargs:
                category.color = kwargs['color']
            
            if 'description' in kwargs:
                category.description = kwargs['description'].strip()
            
            if 'parent_id' in kwargs:
                new_parent = kwargs['parent_id']
                if new_parent != category.parent_id:
                    # Validate new hierarchy
                    old_parent = category.parent_id
                    category.parent_id = new_parent
                    
                    categories = self.get_categories()
                    if not category.validate_hierarchy(categories):
                        category.parent_id = old_parent  # Restore
                        logger.error(f"Moving category would create circular reference")
                        return False
            
            if 'sort_order' in kwargs:
                category.sort_order = kwargs['sort_order']
            
            if 'is_active' in kwargs:
                category.is_active = kwargs['is_active']
            
            # Save changes
            if self.storage.save_category(category):
                self._invalidate_cache()
                logger.info(f"Updated category: {category.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update category {category_id}: {e}")
            return False
    
    def delete_category(self, category_id: str, reassign_to: Optional[str] = None) -> bool:
        """Delete a category with optional reassignment"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                logger.error(f"Category {category_id} not found")
                return False
            
            # Prevent deletion of default categories
            if category.is_default:
                logger.error(f"Cannot delete default category: {category.name}")
                return False
            
            # Check for child categories
            children = self.get_child_categories(category_id)
            if children and not reassign_to:
                logger.error(f"Category has {len(children)} child categories. Specify reassign_to.")
                return False
            
            # Delete from storage
            if self.storage.delete_category(category_id, reassign_to):
                self._invalidate_cache()
                logger.info(f"Deleted category: {category.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete category {category_id}: {e}")
            return False
    
    def get_categories(self, include_inactive: bool = False) -> List[AnnotationCategory]:
        """Get all categories with caching"""
        try:
            # Check cache
            if self._is_cache_valid():
                return list(self._category_cache.values())
            
            # Load from storage
            categories = self.storage.get_categories(include_inactive)
            
            # Update cache
            self._category_cache = {cat.id: cat for cat in categories}
            self._cache_timestamp = datetime.now()
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    def get_category_by_id(self, category_id: str) -> Optional[AnnotationCategory]:
        """Get a specific category by ID"""
        try:
            # Check cache first
            if self._is_cache_valid() and category_id in self._category_cache:
                return self._category_cache[category_id]
            
            # Load from storage
            category = self.storage.get_category_by_id(category_id)
            
            # Update cache
            if category:
                if not self._category_cache:
                    self._category_cache = {}
                self._category_cache[category_id] = category
            
            return category
            
        except Exception as e:
            logger.error(f"Failed to get category {category_id}: {e}")
            return None
    
    def get_category_by_name(self, name: str, parent_id: Optional[str] = None) -> Optional[AnnotationCategory]:
        """Get category by name within a parent"""
        categories = self.get_categories()
        for category in categories:
            if category.name == name and category.parent_id == parent_id:
                return category
        return None
    
    # Hierarchy Management
    def get_category_hierarchy(self) -> Dict[str, List[AnnotationCategory]]:
        """Get category hierarchy as parent_id -> children mapping"""
        try:
            if self._hierarchy_cache and self._is_cache_valid():
                return self._hierarchy_cache
            
            categories = self.get_categories()
            hierarchy = {}
            
            for category in categories:
                parent_id = category.parent_id or "root"
                if parent_id not in hierarchy:
                    hierarchy[parent_id] = []
                hierarchy[parent_id].append(category)
            
            # Sort children by sort_order and name
            for children in hierarchy.values():
                children.sort(key=lambda c: (c.sort_order, c.name))
            
            self._hierarchy_cache = hierarchy
            return hierarchy
            
        except Exception as e:
            logger.error(f"Failed to get category hierarchy: {e}")
            return {}
    
    def get_root_categories(self) -> List[AnnotationCategory]:
        """Get top-level categories (no parent)"""
        hierarchy = self.get_category_hierarchy()
        return hierarchy.get("root", [])
    
    def get_child_categories(self, parent_id: str) -> List[AnnotationCategory]:
        """Get direct children of a category"""
        hierarchy = self.get_category_hierarchy()
        return hierarchy.get(parent_id, [])
    
    def get_category_path(self, category_id: str) -> List[AnnotationCategory]:
        """Get the full path from root to category"""
        try:
            path = []
            current_id = category_id
            
            while current_id:
                category = self.get_category_by_id(current_id)
                if not category:
                    break
                
                path.insert(0, category)
                current_id = category.parent_id
            
            return path
            
        except Exception as e:
            logger.error(f"Failed to get category path for {category_id}: {e}")
            return []
    
    def move_category(self, category_id: str, new_parent_id: Optional[str]) -> bool:
        """Move a category to a new parent"""
        return self.update_category(category_id, parent_id=new_parent_id)
    
    def reorder_categories(self, category_orders: Dict[str, int]) -> bool:
        """Update sort order for multiple categories"""
        try:
            success_count = 0
            for category_id, sort_order in category_orders.items():
                if self.update_category(category_id, sort_order=sort_order):
                    success_count += 1
            
            logger.info(f"Reordered {success_count}/{len(category_orders)} categories")
            return success_count == len(category_orders)
            
        except Exception as e:
            logger.error(f"Failed to reorder categories: {e}")
            return False
    
    # Category Assignment
    def assign_category(self, annotation_id: str, category_id: str, assigned_by: str = "system") -> bool:
        """Assign a category to an annotation"""
        try:
            # Validate category exists
            if not self.get_category_by_id(category_id):
                logger.error(f"Category {category_id} not found")
                return False
            
            # Assign in storage
            if self.storage.assign_category(annotation_id, category_id, assigned_by):
                self._invalidate_cache()  # Category counts may have changed
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to assign category {category_id} to annotation {annotation_id}: {e}")
            return False
    
    def remove_category_assignment(self, annotation_id: str, category_id: str) -> bool:
        """Remove a category assignment"""
        try:
            if self.storage.remove_category_assignment(annotation_id, category_id):
                self._invalidate_cache()  # Category counts may have changed
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove category assignment: {e}")
            return False
    
    def get_annotation_categories(self, annotation_id: str) -> List[AnnotationCategory]:
        """Get all categories assigned to an annotation"""
        return self.storage.get_annotation_categories(annotation_id)
    
    def bulk_assign_categories(self, annotation_ids: List[str], category_ids: List[str],
                              assigned_by: str = "system") -> BulkOperationResult:
        """Assign multiple categories to multiple annotations"""
        operation = BulkOperation(
            operation_type="bulk_categorize",
            annotation_ids=annotation_ids,
            parameters={"category_ids": category_ids, "assigned_by": assigned_by}
        )
        
        result = BulkOperationResult(operation=operation)
        
        try:
            for annotation_id in annotation_ids:
                annotation_success = True
                for category_id in category_ids:
                    if not self.assign_category(annotation_id, category_id, assigned_by):
                        annotation_success = False
                        result.errors.append(f"Failed to assign category {category_id} to {annotation_id}")
                
                if annotation_success:
                    result.success_count += 1
                else:
                    result.failure_count += 1
            
            logger.info(f"Bulk category assignment: {result.success_count} success, {result.failure_count} failed")
            
        except Exception as e:
            logger.error(f"Bulk category assignment failed: {e}")
            result.errors.append(str(e))
        
        return result
    
    # Category Templates and Initialization
    def initialize_default_categories(self) -> bool:
        """Initialize default categories if they don't exist"""
        try:
            existing_categories = self.get_categories()
            existing_names = {cat.name for cat in existing_categories}
            
            created_count = 0
            for default_category in DEFAULT_CATEGORIES:
                if default_category.name not in existing_names:
                    if self.storage.save_category(default_category):
                        created_count += 1
            
            if created_count > 0:
                self._invalidate_cache()
                logger.info(f"Initialized {created_count} default categories")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize default categories: {e}")
            return False
    
    def apply_category_template(self, template_name: str) -> bool:
        """Apply a category template"""
        try:
            if template_name not in CATEGORY_TEMPLATES:
                logger.error(f"Unknown category template: {template_name}")
                return False
            
            template = CATEGORY_TEMPLATES[template_name]
            created_count = 0
            
            for cat_data in template:
                category = AnnotationCategory(
                    name=cat_data["name"],
                    color=cat_data["color"],
                    description=cat_data["description"]
                )
                
                if self.storage.save_category(category):
                    created_count += 1
            
            if created_count > 0:
                self._invalidate_cache()
                logger.info(f"Applied template '{template_name}': created {created_count} categories")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply category template {template_name}: {e}")
            return False
    
    def get_available_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """Get available category templates"""
        return CATEGORY_TEMPLATES.copy()
    
    # Validation and Utilities
    def validate_category_name(self, name: str, parent_id: Optional[str] = None,
                              exclude_id: Optional[str] = None) -> bool:
        """Validate category name for uniqueness and format"""
        if not name or not name.strip():
            return False
        
        return not self._is_name_duplicate(name.strip(), parent_id, exclude_id)
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """Get category usage statistics"""
        try:
            categories = self.get_categories()
            
            stats = {
                "total_categories": len(categories),
                "active_categories": len([c for c in categories if c.is_active]),
                "default_categories": len([c for c in categories if c.is_default]),
                "root_categories": len(self.get_root_categories()),
                "categories_with_children": 0,
                "most_used_category": None,
                "least_used_category": None,
                "average_annotations_per_category": 0
            }
            
            # Calculate hierarchy stats
            hierarchy = self.get_category_hierarchy()
            stats["categories_with_children"] = len([k for k, v in hierarchy.items() if k != "root" and v])
            
            # Find most/least used categories
            active_categories = [c for c in categories if c.is_active and c.annotation_count > 0]
            if active_categories:
                most_used = max(active_categories, key=lambda c: c.annotation_count)
                least_used = min(active_categories, key=lambda c: c.annotation_count)
                
                stats["most_used_category"] = {
                    "name": most_used.name,
                    "count": most_used.annotation_count
                }
                stats["least_used_category"] = {
                    "name": least_used.name,
                    "count": least_used.annotation_count
                }
                
                total_annotations = sum(c.annotation_count for c in active_categories)
                stats["average_annotations_per_category"] = total_annotations / len(active_categories)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get category statistics: {e}")
            return {}
    
    # Cache Management
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        
        # Cache valid for 5 minutes
        cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
        return cache_age < 300
    
    def _invalidate_cache(self):
        """Invalidate category cache"""
        self._category_cache.clear()
        self._hierarchy_cache = None
        self._cache_timestamp = None
    
    def _is_name_duplicate(self, name: str, parent_id: Optional[str] = None,
                          exclude_id: Optional[str] = None) -> bool:
        """Check if category name is duplicate within parent"""
        categories = self.get_categories()
        for category in categories:
            if (category.name.lower() == name.lower() and 
                category.parent_id == parent_id and 
                category.id != exclude_id):
                return True
        return False
    
    def refresh_cache(self):
        """Force refresh of category cache"""
        self._invalidate_cache()
        self.get_categories()  # Reload cache