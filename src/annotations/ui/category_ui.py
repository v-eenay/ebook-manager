"""
Category Management UI Components
User interface elements for category management and assignment
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, QComboBox,
    QFrame, QScrollArea, QGroupBox, QFormLayout, QDialogButtonBox,
    QLineEdit, QTextEdit, QSplitter, QHeaderView, QAbstractItemView,
    QColorDialog, QSpinBox, QCheckBox, QTabWidget, QListWidget,
    QListWidgetItem, QProgressBar, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QPalette, QPixmap,
    QIcon, QStandardItemModel, QStandardItem
)
from qfluentwidgets import (
    PushButton, LineEdit, TextEdit, ComboBox, TreeWidget,
    BodyLabel, CaptionLabel, ScrollArea, ColorPickerButton,
    SpinBox, CheckBox, ListWidget, ProgressBar
)
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from ..models import AnnotationCategory, BulkOperation, BulkOperationResult
from ..category_manager import CategoryManager

logger = logging.getLogger("ebook_reader")

class CategoryTreeWidget(TreeWidget):
    """Enhanced tree widget for displaying category hierarchy"""
    
    category_selected = pyqtSignal(str)  # category_id
    category_edited = pyqtSignal(str)    # category_id
    category_deleted = pyqtSignal(str)   # category_id
    category_moved = pyqtSignal(str, str)  # category_id, new_parent_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_manager = None
        self.categories = []
        self.category_items = {}  # category_id -> QTreeWidgetItem
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the tree widget UI"""
        # Configure tree widget
        self.setHeaderLabels(["Category", "Count", "Color"])
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Configure columns
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Category name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Count
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Color
        header.resizeSection(2, 60)
        
        # Style the tree
        self.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #e3f2fd;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemChanged.connect(self.on_item_changed)
    
    def set_category_manager(self, category_manager: CategoryManager):
        """Set the category manager"""
        self.category_manager = category_manager
        self.refresh_categories()
    
    def refresh_categories(self):
        """Refresh the category tree"""
        if not self.category_manager:
            return
        
        try:
            # Clear existing items
            self.clear()
            self.category_items.clear()
            
            # Get categories and hierarchy
            self.categories = self.category_manager.get_categories()
            hierarchy = self.category_manager.get_category_hierarchy()
            
            # Build tree structure
            self._build_tree_recursive(hierarchy.get("root", []), None)
            
            # Expand all items
            self.expandAll()
            
        except Exception as e:
            logger.error(f"Failed to refresh categories: {e}")
    
    def _build_tree_recursive(self, categories: List[AnnotationCategory], parent_item: Optional[QTreeWidgetItem]):
        """Recursively build tree structure"""
        for category in categories:
            # Create tree item
            if parent_item:
                item = QTreeWidgetItem(parent_item)
            else:
                item = QTreeWidgetItem(self)
            
            # Set item data
            item.setText(0, category.name)
            item.setText(1, str(category.annotation_count))
            item.setData(0, Qt.UserRole, category.id)
            
            # Set category color indicator
            color_widget = self._create_color_indicator(category.color)
            self.setItemWidget(item, 2, color_widget)
            
            # Style item based on category properties
            if category.is_default:
                font = item.font(0)
                font.setBold(True)
                item.setFont(0, font)
                item.setToolTip(0, f"{category.name} (Default Category)")
            else:
                item.setToolTip(0, category.description or category.name)
            
            if not category.is_active:
                # Gray out inactive categories
                for col in range(3):
                    item.setForeground(col, QColor(128, 128, 128))
            
            # Store reference
            self.category_items[category.id] = item
            
            # Add children
            hierarchy = self.category_manager.get_category_hierarchy()
            children = hierarchy.get(category.id, [])
            if children:
                self._build_tree_recursive(children, item)
    
    def _create_color_indicator(self, color: str) -> QWidget:
        """Create a color indicator widget"""
        widget = QWidget()
        widget.setFixedSize(40, 20)
        
        def paint_event(event):
            painter = QPainter(widget)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw color rectangle
            rect = widget.rect().adjusted(2, 2, -2, -2)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(128, 128, 128), 1))
            painter.drawRoundedRect(rect, 3, 3)
        
        widget.paintEvent = paint_event
        return widget
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        category_id = item.data(0, Qt.UserRole)
        if category_id:
            self.category_selected.emit(category_id)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click"""
        category_id = item.data(0, Qt.UserRole)
        if category_id:
            self.category_edited.emit(category_id)
    
    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item changes (for inline editing)"""
        if column == 0:  # Name changed
            category_id = item.data(0, Qt.UserRole)
            new_name = item.text(0)
            
            if category_id and new_name:
                # Validate and update category name
                if self.category_manager.validate_category_name(new_name, exclude_id=category_id):
                    self.category_manager.update_category(category_id, name=new_name)
                else:
                    # Revert to original name
                    category = self.category_manager.get_category_by_id(category_id)
                    if category:
                        item.setText(0, category.name)
                    QMessageBox.warning(self, "Invalid Name", "Category name already exists or is invalid.")
    
    def show_context_menu(self, position: QPoint):
        """Show context menu for category operations"""
        item = self.itemAt(position)
        if not item:
            # Right-click on empty space
            self._show_empty_context_menu(self.mapToGlobal(position))
            return
        
        category_id = item.data(0, Qt.UserRole)
        if not category_id:
            return
        
        category = self.category_manager.get_category_by_id(category_id)
        if not category:
            return
        
        menu = QMenu(self)
        
        # Edit category
        edit_action = menu.addAction("Edit Category")
        edit_action.triggered.connect(lambda: self.category_edited.emit(category_id))
        
        # Add child category
        add_child_action = menu.addAction("Add Child Category")
        add_child_action.triggered.connect(lambda: self._add_child_category(category_id))
        
        menu.addSeparator()
        
        # Move category
        move_menu = menu.addMenu("Move To")
        self._populate_move_menu(move_menu, category_id)
        
        menu.addSeparator()
        
        # Delete category (only if not default)
        if not category.is_default:
            delete_action = menu.addAction("Delete Category")
            delete_action.triggered.connect(lambda: self._confirm_delete_category(category_id))
        
        # Toggle active state
        if category.is_active:
            deactivate_action = menu.addAction("Deactivate Category")
            deactivate_action.triggered.connect(lambda: self._toggle_category_active(category_id, False))
        else:
            activate_action = menu.addAction("Activate Category")
            activate_action.triggered.connect(lambda: self._toggle_category_active(category_id, True))
        
        menu.exec_(self.mapToGlobal(position))
    
    def _show_empty_context_menu(self, position: QPoint):
        """Show context menu for empty space"""
        menu = QMenu(self)
        
        add_action = menu.addAction("Add Root Category")
        add_action.triggered.connect(lambda: self._add_child_category(None))
        
        menu.addSeparator()
        
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_categories)
        
        menu.exec_(position)
    
    def _add_child_category(self, parent_id: Optional[str]):
        """Add a child category"""
        # This will be handled by the parent dialog
        pass
    
    def _populate_move_menu(self, menu: QMenu, category_id: str):
        """Populate move menu with valid parent options"""
        # Add "Move to Root" option
        root_action = menu.addAction("Root Level")
        root_action.triggered.connect(lambda: self.category_moved.emit(category_id, ""))
        
        menu.addSeparator()
        
        # Add other categories as potential parents
        for category in self.categories:
            if category.id != category_id and category.is_active:
                # Check if this would create a circular reference
                path = self.category_manager.get_category_path(category.id)
                if not any(cat.id == category_id for cat in path):
                    action = menu.addAction(category.name)
                    action.triggered.connect(lambda checked, cid=category.id: self.category_moved.emit(category_id, cid))
    
    def _confirm_delete_category(self, category_id: str):
        """Confirm category deletion"""
        category = self.category_manager.get_category_by_id(category_id)
        if not category:
            return
        
        # Check for child categories
        children = self.category_manager.get_child_categories(category_id)
        
        message = f"Are you sure you want to delete the category '{category.name}'?"
        if children:
            message += f"\n\nThis category has {len(children)} child categories that will be moved to the parent level."
        
        if category.annotation_count > 0:
            message += f"\n\nThis category is assigned to {category.annotation_count} annotations. They will be moved to the default category."
        
        reply = QMessageBox.question(
            self, "Delete Category", message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.category_deleted.emit(category_id)
    
    def _toggle_category_active(self, category_id: str, active: bool):
        """Toggle category active state"""
        self.category_manager.update_category(category_id, is_active=active)
        self.refresh_categories()
    
    def get_selected_category_id(self) -> Optional[str]:
        """Get the currently selected category ID"""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(0, Qt.UserRole)
        return None
    
    def select_category(self, category_id: str):
        """Select a specific category"""
        if category_id in self.category_items:
            item = self.category_items[category_id]
            self.setCurrentItem(item)
            self.scrollToItem(item)

class CategoryEditDialog(QDialog):
    """Dialog for creating and editing categories"""
    
    category_saved = pyqtSignal(object)  # AnnotationCategory
    
    def __init__(self, category: Optional[AnnotationCategory] = None,
                 category_manager: Optional[CategoryManager] = None,
                 parent_id: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.category = category
        self.category_manager = category_manager
        self.parent_id = parent_id
        self.is_editing = category is not None
        
        self.init_ui()
        self.setup_connections()
        
        if self.is_editing:
            self.load_category_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Edit Category" if self.is_editing else "Add Category")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = BodyLabel("Category Details")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Form layout
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(8)
        
        # Category name
        self.name_input = LineEdit()
        self.name_input.setPlaceholderText("Enter category name...")
        form_layout.addRow("Name:", self.name_input)
        
        # Category color
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 30)
        self.color_button.clicked.connect(self.choose_color)
        self.current_color = QColor("#808080")
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(100, 30)
        self.color_preview.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        form_layout.addRow("Color:", color_layout)
        
        # Parent category
        self.parent_combo = ComboBox()
        self.parent_combo.addItem("Root Level", None)
        if self.category_manager:
            self._populate_parent_combo()
        form_layout.addRow("Parent:", self.parent_combo)
        
        # Sort order
        self.sort_order_spin = SpinBox()
        self.sort_order_spin.setRange(0, 9999)
        self.sort_order_spin.setValue(0)
        form_layout.addRow("Sort Order:", self.sort_order_spin)
        
        # Description
        self.description_input = TextEdit()
        self.description_input.setPlaceholderText("Optional description...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        # Active checkbox
        self.active_checkbox = CheckBox("Active")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("", self.active_checkbox)
        
        layout.addWidget(form_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setText("Save Category" if self.is_editing else "Add Category")
        
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Update color preview
        self._update_color_preview()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.name_input.textChanged.connect(self.validate_input)
        self.validate_input()  # Initial validation
    
    def _populate_parent_combo(self):
        """Populate parent category combo box"""
        if not self.category_manager:
            return
        
        categories = self.category_manager.get_categories()
        
        for category in categories:
            if category.is_active and (not self.is_editing or category.id != self.category.id):
                # Get full path for display
                path = category.get_full_path(categories)
                self.parent_combo.addItem(path, category.id)
    
    def choose_color(self):
        """Choose category color"""
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self._update_color_preview()
    
    def _update_color_preview(self):
        """Update color preview"""
        color_name = self.current_color.name()
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_name};
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
        """)
        self.color_preview.setStyleSheet(f"""
            background-color: {color_name};
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
    
    def validate_input(self):
        """Validate input and enable/disable OK button"""
        name = self.name_input.text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)
        
        if not name:
            ok_button.setEnabled(False)
            return
        
        # Check name uniqueness
        if self.category_manager:
            parent_id = self.parent_combo.currentData()
            exclude_id = self.category.id if self.is_editing else None
            
            if not self.category_manager.validate_category_name(name, parent_id, exclude_id):
                ok_button.setEnabled(False)
                return
        
        ok_button.setEnabled(True)
    
    def load_category_data(self):
        """Load existing category data into form"""
        if not self.category:
            return
        
        self.name_input.setText(self.category.name)
        self.current_color = QColor(self.category.color)
        self._update_color_preview()
        self.description_input.setPlainText(self.category.description)
        self.sort_order_spin.setValue(self.category.sort_order)
        self.active_checkbox.setChecked(self.category.is_active)
        
        # Set parent
        if self.category.parent_id:
            for i in range(self.parent_combo.count()):
                if self.parent_combo.itemData(i) == self.category.parent_id:
                    self.parent_combo.setCurrentIndex(i)
                    break
    
    def get_category_data(self) -> Dict[str, Any]:
        """Get category data from form"""
        return {
            'name': self.name_input.text().strip(),
            'color': self.current_color.name(),
            'description': self.description_input.toPlainText().strip(),
            'parent_id': self.parent_combo.currentData(),
            'sort_order': self.sort_order_spin.value(),
            'is_active': self.active_checkbox.isChecked()
        }
    
    def accept(self):
        """Handle dialog acceptance"""
        data = self.get_category_data()
        
        try:
            if self.is_editing and self.category:
                # Update existing category
                success = self.category_manager.update_category(self.category.id, **data)
                if success:
                    # Reload category to get updated data
                    updated_category = self.category_manager.get_category_by_id(self.category.id)
                    self.category_saved.emit(updated_category)
                else:
                    QMessageBox.warning(self, "Error", "Failed to update category.")
                    return
            else:
                # Create new category
                category = self.category_manager.create_category(**data)
                if category:
                    self.category_saved.emit(category)
                else:
                    QMessageBox.warning(self, "Error", "Failed to create category.")
                    return
            
            super().accept()
            
        except Exception as e:
            logger.error(f"Failed to save category: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save category: {str(e)}")

class CategoryManagementDialog(QDialog):
    """Main category management dialog"""
    
    def __init__(self, category_manager: CategoryManager, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        
        self.init_ui()
        self.setup_connections()
        self.refresh_categories()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Category Management")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title and description
        title_label = BodyLabel("Category Management")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title_label)
        
        desc_label = CaptionLabel("Organize your annotations with categories. Drag and drop to reorder.")
        desc_label.setStyleSheet("color: #666; margin-bottom: 8px;")
        layout.addWidget(desc_label)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Category tree
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)
        
        # Tree toolbar
        tree_toolbar = QHBoxLayout()
        
        self.add_button = PushButton("Add Category")
        self.add_button.setIcon(QIcon(":/icons/add"))
        tree_toolbar.addWidget(self.add_button)
        
        self.edit_button = PushButton("Edit")
        self.edit_button.setEnabled(False)
        tree_toolbar.addWidget(self.edit_button)
        
        self.delete_button = PushButton("Delete")
        self.delete_button.setEnabled(False)
        tree_toolbar.addWidget(self.delete_button)
        
        tree_toolbar.addStretch()
        
        self.refresh_button = PushButton("Refresh")
        tree_toolbar.addWidget(self.refresh_button)
        
        left_layout.addLayout(tree_toolbar)
        
        # Category tree
        self.category_tree = CategoryTreeWidget()
        self.category_tree.set_category_manager(self.category_manager)
        left_layout.addWidget(self.category_tree)
        
        content_splitter.addWidget(left_panel)
        
        # Right panel - Category details and statistics
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)
        
        # Category details
        details_group = QGroupBox("Category Details")
        details_layout = QFormLayout(details_group)
        
        self.details_name = QLabel("-")
        self.details_name.setStyleSheet("font-weight: bold;")
        details_layout.addRow("Name:", self.details_name)
        
        self.details_color = QLabel()
        self.details_color.setFixedSize(40, 20)
        details_layout.addRow("Color:", self.details_color)
        
        self.details_parent = QLabel("-")
        details_layout.addRow("Parent:", self.details_parent)
        
        self.details_count = QLabel("-")
        details_layout.addRow("Annotations:", self.details_count)
        
        self.details_created = QLabel("-")
        details_layout.addRow("Created:", self.details_created)
        
        right_layout.addWidget(details_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Select a category to view statistics")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        right_layout.addWidget(stats_group)
        
        # Templates
        templates_group = QGroupBox("Category Templates")
        templates_layout = QVBoxLayout(templates_group)
        
        template_desc = CaptionLabel("Apply predefined category sets for common use cases:")
        templates_layout.addWidget(template_desc)
        
        template_buttons_layout = QHBoxLayout()
        
        self.academic_template_btn = PushButton("Academic")
        self.academic_template_btn.clicked.connect(lambda: self.apply_template("academic"))
        template_buttons_layout.addWidget(self.academic_template_btn)
        
        self.business_template_btn = PushButton("Business")
        self.business_template_btn.clicked.connect(lambda: self.apply_template("business"))
        template_buttons_layout.addWidget(self.business_template_btn)
        
        self.learning_template_btn = PushButton("Learning")
        self.learning_template_btn.clicked.connect(lambda: self.apply_template("learning"))
        template_buttons_layout.addWidget(self.learning_template_btn)
        
        templates_layout.addLayout(template_buttons_layout)
        
        right_layout.addWidget(templates_group)
        
        right_layout.addStretch()
        
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([500, 300])
        
        layout.addWidget(content_splitter)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Close, Qt.Horizontal)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Tree signals
        self.category_tree.category_selected.connect(self.on_category_selected)
        self.category_tree.category_edited.connect(self.edit_category)
        self.category_tree.category_deleted.connect(self.delete_category)
        self.category_tree.category_moved.connect(self.move_category)
        
        # Button signals
        self.add_button.clicked.connect(self.add_category)
        self.edit_button.clicked.connect(self.edit_selected_category)
        self.delete_button.clicked.connect(self.delete_selected_category)
        self.refresh_button.clicked.connect(self.refresh_categories)
    
    def refresh_categories(self):
        """Refresh category display"""
        self.category_tree.refresh_categories()
        self.update_details_panel(None)
    
    def on_category_selected(self, category_id: str):
        """Handle category selection"""
        category = self.category_manager.get_category_by_id(category_id)
        self.update_details_panel(category)
        
        # Enable/disable buttons
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(category and not category.is_default)
    
    def update_details_panel(self, category: Optional[AnnotationCategory]):
        """Update the details panel"""
        if not category:
            self.details_name.setText("-")
            self.details_color.setStyleSheet("background-color: transparent; border: 1px solid #ccc;")
            self.details_parent.setText("-")
            self.details_count.setText("-")
            self.details_created.setText("-")
            self.stats_label.setText("Select a category to view statistics")
            return
        
        # Update details
        self.details_name.setText(category.name)
        self.details_color.setStyleSheet(f"""
            background-color: {category.color};
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        
        # Parent category
        if category.parent_id:
            parent = self.category_manager.get_category_by_id(category.parent_id)
            self.details_parent.setText(parent.name if parent else "Unknown")
        else:
            self.details_parent.setText("Root Level")
        
        self.details_count.setText(str(category.annotation_count))
        self.details_created.setText(category.created_at.strftime("%Y-%m-%d %H:%M"))
        
        # Update statistics
        stats_text = f"Category: {category.name}\n"
        stats_text += f"Annotations: {category.annotation_count}\n"
        stats_text += f"Status: {'Active' if category.is_active else 'Inactive'}\n"
        stats_text += f"Type: {'Default' if category.is_default else 'Custom'}\n"
        
        if category.description:
            stats_text += f"Description: {category.description}\n"
        
        # Add hierarchy info
        path = self.category_manager.get_category_path(category.id)
        if len(path) > 1:
            path_names = " > ".join(cat.name for cat in path)
            stats_text += f"Path: {path_names}\n"
        
        children = self.category_manager.get_child_categories(category.id)
        if children:
            stats_text += f"Child Categories: {len(children)}\n"
        
        self.stats_label.setText(stats_text)
    
    def add_category(self):
        """Add a new category"""
        selected_id = self.category_tree.get_selected_category_id()
        
        dialog = CategoryEditDialog(
            category=None,
            category_manager=self.category_manager,
            parent_id=selected_id,
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_categories()
    
    def edit_category(self, category_id: str):
        """Edit a category"""
        category = self.category_manager.get_category_by_id(category_id)
        if not category:
            return
        
        dialog = CategoryEditDialog(
            category=category,
            category_manager=self.category_manager,
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_categories()
            self.on_category_selected(category_id)  # Refresh details
    
    def edit_selected_category(self):
        """Edit the selected category"""
        selected_id = self.category_tree.get_selected_category_id()
        if selected_id:
            self.edit_category(selected_id)
    
    def delete_category(self, category_id: str):
        """Delete a category"""
        if self.category_manager.delete_category(category_id):
            self.refresh_categories()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete category.")
    
    def delete_selected_category(self):
        """Delete the selected category"""
        selected_id = self.category_tree.get_selected_category_id()
        if selected_id:
            self.delete_category(selected_id)
    
    def move_category(self, category_id: str, new_parent_id: str):
        """Move a category to a new parent"""
        parent_id = new_parent_id if new_parent_id else None
        if self.category_manager.move_category(category_id, parent_id):
            self.refresh_categories()
        else:
            QMessageBox.warning(self, "Error", "Failed to move category.")
    
    def apply_template(self, template_name: str):
        """Apply a category template"""
        reply = QMessageBox.question(
            self, "Apply Template",
            f"Apply the {template_name.title()} category template?\n\n"
            "This will add predefined categories for this use case.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.category_manager.apply_category_template(template_name):
                self.refresh_categories()
                QMessageBox.information(self, "Success", f"{template_name.title()} template applied successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Failed to apply {template_name} template.")