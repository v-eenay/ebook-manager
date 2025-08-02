"""
Main Window for Modern EBook Reader
Implements a clean, minimal interface for document viewing.
"""

import os
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                QToolBar, QPushButton, QLabel, QScrollArea, 
                                QFileDialog, QMessageBox, QTabWidget, QSplitter)
    from PyQt6.QtCore import Qt, QSize, pyqtSignal
    from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont, QPalette, QColor
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                QToolBar, QPushButton, QLabel, QScrollArea, 
                                QFileDialog, QMessageBox, QTabWidget, QSplitter)
    from PyQt5.QtCore import Qt, QSize, pyqtSignal
    from PyQt5.QtGui import QPixmap, QIcon, QFont, QPalette, QColor
    QT_VERSION = 5

from .document_viewer import DocumentViewer
from .welcome_widget import WelcomeWidget
from readers.document_manager import DocumentManager


class MainWindow(QMainWindow):
    """Main application window with modern, minimal design."""
    
    def __init__(self):
        super().__init__()
        self.document_manager = DocumentManager()
        self.current_document = None
        
        self.init_ui()
        self.apply_modern_theme()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Modern EBook Reader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create tab widget for document viewing
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(False)
        
        # Create welcome tab
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.open_file_requested.connect(self.open_file)
        self.tab_widget.addTab(self.welcome_widget, "Welcome")
        
        # Create document viewer
        self.document_viewer = DocumentViewer()
        self.tab_widget.addTab(self.document_viewer, "Reader")
        
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.create_status_bar()
        
        # Initially show welcome tab
        self.tab_widget.setCurrentIndex(0)
        
    def create_toolbar(self):
        """Create the main toolbar with minimal design."""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        if QT_VERSION == 6:
            from PyQt6.QtCore import Qt
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Open file action
        open_action = QAction("Open Document", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Navigation actions (initially disabled)
        self.prev_action = QAction("Previous", self)
        self.prev_action.setShortcut("Left")
        self.prev_action.setEnabled(False)
        self.prev_action.triggered.connect(self.previous_page)
        toolbar.addAction(self.prev_action)
        
        self.next_action = QAction("Next", self)
        self.next_action.setShortcut("Right")
        self.next_action.setEnabled(False)
        self.next_action.triggered.connect(self.next_page)
        toolbar.addAction(self.next_action)
        
        toolbar.addSeparator()
        
        # Page info label
        self.page_label = QLabel("No document")
        toolbar.addWidget(self.page_label)
        
        toolbar.addSeparator()
        
        # Zoom actions (initially disabled)
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.setEnabled(False)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(self.zoom_out_action)
        
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.setEnabled(False)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(self.zoom_in_action)
        
        # Zoom level label
        self.zoom_label = QLabel("100%")
        toolbar.addWidget(self.zoom_label)
        
    def create_status_bar(self):
        """Create a minimal status bar."""
        status_bar = self.statusBar()
        status_bar.showMessage("Ready")
        
    def apply_modern_theme(self):
        """Apply modern, minimal styling to the application."""
        # Set a clean, modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FAFAFA;
                color: #212121;
            }
            QToolBar {
                background-color: #F5F5F5;
                border: none;
                spacing: 8px;
                padding: 4px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 2px;
            }
            QToolBar QToolButton:hover {
                background-color: #E0E0E0;
                border-color: #BDBDBD;
            }
            QToolBar QToolButton:pressed {
                background-color: #D0D0D0;
            }
            QTabWidget::pane {
                border: none;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                border: none;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom: 2px solid #4285F4;
            }
            QTabBar::tab:hover {
                background-color: #E8E8E8;
            }
            QStatusBar {
                background-color: #F5F5F5;
                border-top: 1px solid #E0E0E0;
                color: #666666;
            }
        """)
        
    def setup_connections(self):
        """Set up signal connections."""
        self.document_viewer.page_changed.connect(self.update_page_info)
        self.document_viewer.zoom_changed.connect(self.update_zoom_info)
        
    def open_file(self):
        """Open a file dialog to select a document."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported (*.pdf *.epub *.mobi);;PDF Files (*.pdf);;EPUB Files (*.epub);;MOBI Files (*.mobi)"
        )
        
        if file_path:
            self.load_document(file_path)
            
    def load_document(self, file_path):
        """Load a document and switch to reader view."""
        try:
            # Load the document
            self.current_document = self.document_manager.load_document(file_path)
            
            # Set up the document viewer
            self.document_viewer.set_document(self.current_document)
            
            # Close welcome tab if it exists
            if self.tab_widget.count() > 1 and self.tab_widget.tabText(0) == "Welcome":
                self.tab_widget.removeTab(0)
            
            # Switch to reader tab
            self.tab_widget.setCurrentIndex(0)
            
            # Enable navigation and zoom controls
            self.enable_document_controls(True)
            
            # Update window title
            filename = Path(file_path).name
            self.setWindowTitle(f"Modern EBook Reader - {filename}")
            
            # Update status
            self.statusBar().showMessage(f"Loaded: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document:\n{str(e)}")
            
    def enable_document_controls(self, enabled):
        """Enable or disable document-related controls."""
        self.prev_action.setEnabled(enabled)
        self.next_action.setEnabled(enabled)
        self.zoom_in_action.setEnabled(enabled)
        self.zoom_out_action.setEnabled(enabled)
        
    def previous_page(self):
        """Navigate to the previous page."""
        if self.document_viewer:
            self.document_viewer.previous_page()
            
    def next_page(self):
        """Navigate to the next page."""
        if self.document_viewer:
            self.document_viewer.next_page()
            
    def zoom_in(self):
        """Zoom in on the document."""
        if self.document_viewer:
            self.document_viewer.zoom_in()
            
    def zoom_out(self):
        """Zoom out on the document."""
        if self.document_viewer:
            self.document_viewer.zoom_out()
            
    def update_page_info(self, current_page, total_pages):
        """Update the page information display."""
        self.page_label.setText(f"Page {current_page} of {total_pages}")
        
    def update_zoom_info(self, zoom_level):
        """Update the zoom level display."""
        self.zoom_label.setText(f"{int(zoom_level * 100)}%")
        
    def dragEnterEvent(self, event):
        """Handle drag enter events for file dropping."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        """Handle file drop events."""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            file_path = files[0]
            if file_path.lower().endswith(('.pdf', '.epub', '.mobi')):
                self.load_document(file_path)
            else:
                QMessageBox.warning(self, "Unsupported Format", 
                                  "Please drop a PDF, EPUB, or MOBI file.")
