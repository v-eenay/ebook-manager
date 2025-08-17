"""
Category Assignment UI Components
Interface elements for assigning categories to annotations
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QComboBox,
    QFrame, QScrollArea, QGroupBox, QFormLayout, QDialogButtonBox,
    QLineEdit, QCheckBox, QButtonGroup, QRadioButton, QProgressBar,
    QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QPalette, QPixmap,
    QIcon, QStandardItemModel, QStandardItem
)
from qfluentwidgets import (
    PushButton, LineEdit, ComboBox, CheckBox, ListWidget,
    BodyLabel, CaptionLabel, ScrollArea, ProgressBar
)
import logging
from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from ..models import AnnotationCategory, Annotation, BulkOperation, BulkOperationResult
from ..category_manager import CategoryManager

logger = logging.getLogger("ebook_reader")

class CategorySelector(QWidget):
    """Widget for selecting categories with hierarchy support"""
    
    categories_changed = pyqtSignal(list)  # List of category IDs
    
    def __init__(self, category_manager: CategoryManager, 
                 multi_select: bool = True, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.multi_select = multi_select
        self.selected_categories = set()
        
        self.init_ui()
        self.setup_connections()
        self.refresh_categories()
    
    def init_ui(self):
        """Initialize the selector UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Search box
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Search categories...")
        layout.addWidget(self.search_input)
        
        # Category list
        self.category_list = ListWidget()
        self.category_list.setMaximumHeight(200)
        layout.addWidget(self.category_list)
        
        # Selected categories display (for multi-select)
        if self.multi_select:
            self.selected_label = CaptionLabel("Selected: None")
            self.selected_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(self.selected_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_input.textChanged.connect(self.filter_categories)
        self.category_list.itemChanged.connect(self.on_item_changed)
        if not self.multi_select:
            self.category_list.itemClicked.connect(self.on_item_clicked)
    
    def refresh_categories(self):
        """Refresh the category list"""
        try:
            self.category_list.clear()
            categories = self.category_manager.get_categories()
            
            # Sort categories by hierarchy and name
            root_categories = [cat for cat in categories if not cat.parent_id]
            root_categories.sort(key=lambda c: (c.sort_order, c.name))
            
            # Add categories with hierarchy indication
            self._add_categories_recursive(root_categories, categories, 0)
            
        except Exception as e:
            logger.error(f"Failed to refresh categories: {e}")
    
    def _add_categories_recursive(self, categories: List[AnnotationCategory], 
                                 all_categories: List[AnnotationCategory], level: int):
        """Recursively add categories with indentation"""
        for category in categories:
            if not category.is_active:
                continue
            
            # Create list item
            item = QListWidgetItem()
            
            # Create display text with indentation
            indent = "  " * level
            display_text = f"{indent}{category.name}"
            if category.annotation_count > 0:
                display_text += f" ({category.annotation_count})"
            
            item.setText(display_text)
            item.setData(Qt.UserRole, category.id)
            
            # Set item properties
            if self.multi_select:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
            
            # Color indicator
            color_indicator = self._create_color_indicator(category.color)
            item.setIcon(color_indicator)
            
            # Style based on category properties
            if category.is_default:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.category_list.addItem(item)
            
            # Add children
            children = [cat for cat in all_categories if cat.parent_id == category.id]
            children.sort(key=lambda c: (c.sort_order, c.name))
            if children:
                self._add_categories_recursive(children, all_categories, level + 1)
    
    def _create_color_indicator(self, color: str) -> QIcon:
        """Create a color indicator icon"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw color circle
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        painter.drawEllipse(2, 2, 12, 12)
        
        painter.end()
        return QIcon(pixmap)
    
    def filter_categories(self, text: str):
        """Filter categories based on search text"""
        text = text.lower()
        
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            category_id = item.data(Qt.UserRole)
            category = self.category_manager.get_category_by_id(category_id)
            
            if category:
                # Check if category matches search
                matches = (text in category.name.lower() or 
                          text in category.description.lower())
                item.setHidden(not matches and text)
    
    def on_item_changed(self, item: QListWidgetItem):
        """Handle item check state change"""
        if not self.multi_select:
            return
        
        category_id = item.data(Qt.UserRole)
        if item.checkState() == Qt.Checked:
            self.selected_categories.add(category_id)
        else:
            self.selected_categories.discard(category_id)
        
        self._update_selected_display()
        self.categories_changed.emit(list(self.selected_categories))
    
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click for single select"""
        if self.multi_select:
            return
        
        category_id = item.data(Qt.UserRole)
        self.selected_categories = {category_id}
        self.categories_changed.emit([category_id])
    
    def _update_selected_display(self):
        """Update selected categories display"""
        if not self.multi_select or not hasattr(self, 'selected_label'):
            return
        
        if not self.selected_categories:
            self.selected_label.setText("Selected: None")
        else:
            count = len(self.selected_categories)
            if count == 1:
                category_id = next(iter(self.selected_categories))
                category = self.category_manager.get_category_by_id(category_id)
                name = category.name if category else "Unknown"
                self.selected_label.setText(f"Selected: {name}")
            else:
                self.selected_label.setText(f"Selected: {count} categories")
    
    def set_selected_categories(self, category_ids: List[str]):
        """Set the selected categories"""
        self.selected_categories = set(category_ids)
        
        # Update UI
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            category_id = item.data(Qt.UserRole)
            
            if self.multi_select:
                item.setCheckState(Qt.Checked if category_id in self.selected_categories else Qt.Unchecked)
            else:
                item.setSelected(category_id in self.selected_categories)
        
        self._update_selected_display()
    
    def get_selected_categories(self) -> List[str]:
        """Get the selected category IDs"""
        return list(self.selected_categories)
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_categories.clear()
        
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            if self.multi_select:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setSelected(False)
        
        self._update_selected_display()

class CategoryAssignmentDialog(QDialog):
    """Dialog for assigning categories to annotations"""
    
    categories_assigned = pyqtSignal(list, list)  # annotation_ids, category_ids
    
    def __init__(self, annotation_ids: List[str], category_manager: CategoryManager,
                 annotation_manager=None, parent=None):
        super().__init__(parent)
        self.annotation_ids = annotation_ids
        self.category_manager = category_manager
        self.annotation_manager = annotation_manager
        self.current_categories = set()
        
        self.init_ui()
        self.setup_connections()
        self.load_current_categories()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Assign Categories")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title and info
        if len(self.annotation_ids) == 1:
            title_text = "Assign Categories to Annotation"
        else:
            title_text = f"Assign Categories to {len(self.annotation_ids)} Annotations"
        
        title_label = BodyLabel(title_text)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Current categories info
        self.current_info_label = CaptionLabel("Loading current categories...")
        layout.addWidget(self.current_info_label)
        
        # Category selector
        selector_group = QGroupBox("Select Categories")
        selector_layout = QVBoxLayout(selector_group)
        
        self.category_selector = CategorySelector(self.category_manager, multi_select=True)
        selector_layout.addWidget(self.category_selector)
        
        layout.addWidget(selector_group)
        
        # Assignment options
        options_group = QGroupBox("Assignment Options")
        options_layout = QVBoxLayout(options_group)
        
        self.replace_radio = QRadioButton("Replace existing categories")
        self.add_radio = QRadioButton("Add to existing categories")
        self.remove_radio = QRadioButton("Remove selected categories")
        
        self.replace_radio.setChecked(True)  # Default option
        
        options_layout.addWidget(self.replace_radio)
        options_layout.addWidget(self.add_radio)
        options_layout.addWidget(self.remove_radio)
        
        layout.addWidget(options_group)
        
        # Progress bar (hidden initially)
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setText("Assign Categories")
        
        layout.addWidget(button_box)
        
        # Connect buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.category_selector.categories_changed.connect(self.on_categories_changed)
        self.replace_radio.toggled.connect(self.on_option_changed)
        self.add_radio.toggled.connect(self.on_option_changed)
        self.remove_radio.toggled.connect(self.on_option_changed)
    
    def load_current_categories(self):
        """Load current categories for the annotations"""
        if not self.annotation_manager:
            self.current_info_label.setText("Current categories: Unknown")
            return
        
        try:
            # Get categories for all annotations
            all_categories = set()
            common_categories = None
            
            for annotation_id in self.annotation_ids:
                categories = self.annotation_manager.get_annotation_categories(annotation_id)
                category_ids = {cat.id for cat in categories}
                all_categories.update(category_ids)
                
                if common_categories is None:
                    common_categories = category_ids
                else:
                    common_categories &= category_ids
            
            self.current_categories = all_categories
            
            # Update info label
            if not all_categories:
                self.current_info_label.setText("Current categories: None")
            elif len(self.annotation_ids) == 1:
                category_names = []
                for cat_id in all_categories:
                    category = self.category_manager.get_category_by_id(cat_id)
                    if category:
                        category_names.append(category.name)
                
                if category_names:
                    self.current_info_label.setText(f"Current categories: {', '.join(category_names)}")
                else:
                    self.current_info_label.setText("Current categories: None")
            else:
                common_count = len(common_categories) if common_categories else 0
                total_count = len(all_categories)
                self.current_info_label.setText(
                    f"Categories: {common_count} common, {total_count} total across all annotations"
                )
            
            # Pre-select current categories if replacing
            if self.replace_radio.isChecked():
                self.category_selector.set_selected_categories(list(common_categories or []))
            
        except Exception as e:
            logger.error(f"Failed to load current categories: {e}")
            self.current_info_label.setText("Current categories: Error loading")
    
    def on_categories_changed(self, category_ids: List[str]):
        """Handle category selection changes"""
        # Update OK button state
        has_selection = len(category_ids) > 0
        self.ok_button.setEnabled(has_selection or self.remove_radio.isChecked())
    
    def on_option_changed(self):
        """Handle assignment option changes"""
        if self.replace_radio.isChecked():
            # Pre-select common categories
            self.load_current_categories()
        elif self.add_radio.isChecked():
            # Clear selection for adding
            self.category_selector.clear_selection()
        elif self.remove_radio.isChecked():
            # Pre-select current categories for removal
            self.category_selector.set_selected_categories(list(self.current_categories))
        
        # Update OK button
        selected = self.category_selector.get_selected_categories()
        self.ok_button.setEnabled(len(selected) > 0 or self.remove_radio.isChecked())
    
    def accept(self):
        """Handle dialog acceptance"""
        selected_categories = self.category_selector.get_selected_categories()
        
        if not selected_categories and not self.remove_radio.isChecked():
            QMessageBox.warning(self, "No Selection", "Please select at least one category.")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.ok_button.setEnabled(False)
        
        try:
            # Perform assignment based on selected option
            if self.replace_radio.isChecked():
                success = self._replace_categories(selected_categories)
            elif self.add_radio.isChecked():
                success = self._add_categories(selected_categories)
            elif self.remove_radio.isChecked():
                success = self._remove_categories(selected_categories)
            else:
                success = False
            
            if success:
                self.categories_assigned.emit(self.annotation_ids, selected_categories)
                super().accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to assign categories.")
                
        except Exception as e:
            logger.error(f"Failed to assign categories: {e}")
            QMessageBox.critical(self, "Error", f"Failed to assign categories: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)
            self.ok_button.setEnabled(True)
    
    def _replace_categories(self, category_ids: List[str]) -> bool:
        """Replace all categories with selected ones"""
        try:
            success_count = 0
            
            for annotation_id in self.annotation_ids:
                # Remove all current categories
                current_categories = self.annotation_manager.get_annotation_categories(annotation_id)
                for category in current_categories:
                    self.annotation_manager.remove_category_from_annotation(annotation_id, category.id)
                
                # Add new categories
                for category_id in category_ids:
                    if self.annotation_manager.assign_category_to_annotation(annotation_id, category_id):
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to replace categories: {e}")
            return False
    
    def _add_categories(self, category_ids: List[str]) -> bool:
        """Add categories to existing ones"""
        try:
            success_count = 0
            
            for annotation_id in self.annotation_ids:
                for category_id in category_ids:
                    if self.annotation_manager.assign_category_to_annotation(annotation_id, category_id):
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to add categories: {e}")
            return False
    
    def _remove_categories(self, category_ids: List[str]) -> bool:
        """Remove selected categories"""
        try:
            success_count = 0
            
            for annotation_id in self.annotation_ids:
                for category_id in category_ids:
                    if self.annotation_manager.remove_category_from_annotation(annotation_id, category_id):
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to remove categories: {e}")
            return False

class QuickCategoryAssignment(QWidget):
    """Quick category assignment widget for annotation panels"""
    
    category_assigned = pyqtSignal(str, str)  # annotation_id, category_id
    category_removed = pyqtSignal(str, str)   # annotation_id, category_id
    
    def __init__(self, annotation_id: str, category_manager: CategoryManager,
                 annotation_manager=None, parent=None):
        super().__init__(parent)
        self.annotation_id = annotation_id
        self.category_manager = category_manager
        self.annotation_manager = annotation_manager
        self.current_categories = []
        
        self.init_ui()
        self.setup_connections()
        self.refresh_categories()
    
    def init_ui(self):
        """Initialize the widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Category dropdown
        self.category_combo = ComboBox()
        self.category_combo.setPlaceholderText("Add category...")
        self.category_combo.setMinimumWidth(120)
        layout.addWidget(self.category_combo)
        
        # Add button
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(24, 24)
        self.add_button.setToolTip("Add selected category")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.add_button)
        
        # Current categories display
        self.categories_layout = QHBoxLayout()
        self.categories_layout.setSpacing(2)
        layout.addLayout(self.categories_layout)
        
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.add_button.clicked.connect(self.add_selected_category)
        self.category_combo.currentTextChanged.connect(self.on_combo_changed)
    
    def refresh_categories(self):
        """Refresh available categories"""
        try:
            # Clear combo
            self.category_combo.clear()
            self.category_combo.addItem("Select category...", None)
            
            # Add available categories
            categories = self.category_manager.get_categories()
            for category in categories:
                if category.is_active:
                    self.category_combo.addItem(category.name, category.id)
            
            # Load current categories
            self.load_current_categories()
            
        except Exception as e:
            logger.error(f"Failed to refresh categories: {e}")
    
    def load_current_categories(self):
        """Load and display current categories"""
        if not self.annotation_manager:
            return
        
        try:
            self.current_categories = self.annotation_manager.get_annotation_categories(self.annotation_id)
            self.update_categories_display()
            
        except Exception as e:
            logger.error(f"Failed to load current categories: {e}")
    
    def update_categories_display(self):
        """Update the current categories display"""
        # Clear existing category widgets
        while self.categories_layout.count():
            child = self.categories_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add category tags
        for category in self.current_categories:
            tag = self._create_category_tag(category)
            self.categories_layout.addWidget(tag)
    
    def _create_category_tag(self, category: AnnotationCategory) -> QWidget:
        """Create a category tag widget"""
        tag = QWidget()
        tag.setFixedHeight(20)
        
        layout = QHBoxLayout(tag)
        layout.setContentsMargins(6, 2, 2, 2)
        layout.setSpacing(4)
        
        # Category name
        name_label = QLabel(category.name)
        name_label.setStyleSheet(f"""
            color: white;
            font-size: 10px;
            font-weight: bold;
        """)
        layout.addWidget(name_label)
        
        # Remove button
        remove_button = QPushButton("×")
        remove_button.setFixedSize(14, 14)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_category(category.id))
        layout.addWidget(remove_button)
        
        # Style the tag
        tag.setStyleSheet(f"""
            QWidget {{
                background-color: {category.color};
                border-radius: 10px;
            }}
        """)
        
        return tag
    
    def on_combo_changed(self, text: str):
        """Handle combo box selection change"""
        self.add_button.setEnabled(self.category_combo.currentData() is not None)
    
    def add_selected_category(self):
        """Add the selected category"""
        category_id = self.category_combo.currentData()
        if not category_id:
            return
        
        # Check if already assigned
        current_ids = {cat.id for cat in self.current_categories}
        if category_id in current_ids:
            QMessageBox.information(self, "Already Assigned", "This category is already assigned.")
            return
        
        # Assign category
        if self.annotation_manager:
            if self.annotation_manager.assign_category_to_annotation(self.annotation_id, category_id):
                self.category_assigned.emit(self.annotation_id, category_id)
                self.load_current_categories()  # Refresh display
            else:
                QMessageBox.warning(self, "Error", "Failed to assign category.")
        
        # Reset combo
        self.category_combo.setCurrentIndex(0)
    
    def remove_category(self, category_id: str):
        """Remove a category"""
        if self.annotation_manager:
            if self.annotation_manager.remove_category_from_annotation(self.annotation_id, category_id):
                self.category_removed.emit(self.annotation_id, category_id)
                self.load_current_categories()  # Refresh display
            else:
                QMessageBox.warning(self, "Error", "Failed to remove category.")

class CategoryIndicator(QWidget):
    """Visual indicator showing annotation categories"""
    
    def __init__(self, categories: List[AnnotationCategory], parent=None):
        super().__init__(parent)
        self.categories = categories
        self.setFixedHeight(20)
        self.setMinimumWidth(60)
        
        # Create tooltip
        if categories:
            tooltip_text = "Categories: " + ", ".join(cat.name for cat in categories)
            self.setToolTip(tooltip_text)
    
    def paintEvent(self, event):
        """Paint category color indicators"""
        if not self.categories:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate segment width
        width = self.width()
        height = self.height()
        segment_width = width / len(self.categories)
        
        # Draw color segments
        for i, category in enumerate(self.categories):
            x = int(i * segment_width)
            segment_rect = painter.drawRect(x, 0, int(segment_width), height)
            
            painter.setBrush(QBrush(QColor(category.color)))
            painter.setPen(QPen(QColor(128, 128, 128), 1))
            painter.drawRect(x, 0, int(segment_width), height)
    
    def update_categories(self, categories: List[AnnotationCategory]):
        """Update the categories to display"""
        self.categories = categories
        
        # Update tooltip
        if categories:
            tooltip_text = "Categories: " + ", ".join(cat.name for cat in categories)
            self.setToolTip(tooltip_text)
        else:
            self.setToolTip("No categories")
        
        self.update()  # Trigger repaint