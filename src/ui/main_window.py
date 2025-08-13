"""
Main Window for Modern EBook Reader
Clean, minimal, professional design focused on document viewing.
"""

from pathlib import Path

# Force PyQt5 for compatibility
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget, QAction
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
QT_VERSION = 5

# Import Point for type hints (will be imported when needed)
try:
    from annotations.models import Point
except ImportError:
    Point = None

# Logger will be imported inside methods to avoid early initialization

class MainWindow(QMainWindow):
    """Main window with clean, minimal design focused on document viewing."""

    def __init__(self):
        super().__init__()
        self.current_document = None
        self.document_manager = None
        self.search_engine = None
        self.search_indexer = None
        self.annotation_manager = None
        self.bookmark_sidebar = None
        self.annotation_toolbar = None
        self.init_search()
        self.init_annotations()
        self.init_ui()
        self.setup_shortcuts()
        self.setup_drag_drop()

    def init_search(self):
        """Initialize search functionality"""
        try:
            from search.search_engine import SearchEngine
            from search.indexer import DocumentIndexer
            
            self.search_engine = SearchEngine()
            self.search_indexer = DocumentIndexer(self.search_engine)
        except Exception as e:
            # Search functionality is optional
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.warning(f"Search functionality not available: {e}")
            self.search_engine = None
            self.search_indexer = None

    def init_annotations(self):
        """Initialize annotation functionality"""
        try:
            from annotations.annotation_manager import AnnotationManager
            
            self.annotation_manager = AnnotationManager()
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info("Annotation system initialized")
        except Exception as e:
            # Annotation functionality is optional
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.warning(f"Annotation functionality not available: {e}")
            self.annotation_manager = None

    def init_ui(self):
        """Initialize the clean, minimal user interface."""
        self.setWindowTitle("Modern EBook Reader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create status bar for reading progress
        self.create_status_bar()
        main_layout.addWidget(self.status_bar)

        # Create welcome page
        self.create_welcome_page()

        # Create document viewer page
        self.create_document_page()
        
        # Create search page
        self.create_search_page()

        # Start with welcome page
        self.stacked_widget.setCurrentIndex(0)

    def create_welcome_page(self):
        """Create a clean, minimal welcome page."""
        from ui.welcome_widget import WelcomeWidget
        
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.open_file_requested.connect(self.open_file)
        self.welcome_widget.open_recent_requested.connect(self.load_document)
        
        self.stacked_widget.addWidget(self.welcome_widget)

    def create_document_page(self):
        """Create the document viewer page."""
        document_widget = QWidget()
        layout = QVBoxLayout(document_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create minimal toolbar
        self.create_minimal_toolbar(layout)
        
        # Create annotation toolbar if available
        self.create_annotation_toolbar(layout)

        # Create main content area with sidebar support
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create bookmark sidebar (initially hidden)
        self.create_bookmark_sidebar(content_layout)

        # Create document viewer (lazy loading)
        self.document_viewer = None
        self.document_viewer_container = QWidget()
        self.document_viewer_layout = QVBoxLayout(self.document_viewer_container)
        self.document_viewer_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.document_viewer_container)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        self.stacked_widget.addWidget(document_widget)

    def create_search_page(self):
        """Create the search page."""
        if not self.search_engine:
            return  # Search not available
        
        try:
            from search.search_ui import SearchWidget
            
            self.search_widget = SearchWidget(self.search_engine)
            self.search_widget.document_requested.connect(self.open_search_result)
            
            self.stacked_widget.addWidget(self.search_widget)
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to create search page: {e}")

    def create_minimal_toolbar(self, parent_layout):
        """Create an extremely minimal, professional toolbar using standard Qt widgets."""
        try:
            from PyQt5.QtWidgets import QPushButton, QLabel
        except ImportError:
            from PyQt6.QtWidgets import QPushButton, QLabel

        # Create ultra-minimal toolbar - reduced height for more document space
        toolbar = QWidget()
        toolbar.setFixedHeight(45)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
                border-bottom: 1px solid #E5E5E5;
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 8, 15, 8)
        toolbar_layout.setSpacing(8)

        # Essential buttons only - text-based for compatibility
        home_btn = QPushButton("Home")
        home_btn.setToolTip("Home (Alt+H)")
        home_btn.clicked.connect(self.show_welcome)
        toolbar_layout.addWidget(home_btn)

        open_btn = QPushButton("Open")
        open_btn.setToolTip("Open Document (Ctrl+O)")
        open_btn.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_btn)

        # Minimal separator
        sep1 = QWidget()
        sep1.setFixedSize(1, 25)
        sep1.setStyleSheet("background-color: #D5D5D5;")
        toolbar_layout.addWidget(sep1)

        # Navigation - essential for document viewing
        prev_btn = QPushButton("◀")
        prev_btn.setToolTip("Previous Page (←)")
        prev_btn.clicked.connect(self.previous_page)
        toolbar_layout.addWidget(prev_btn)

        next_btn = QPushButton("▶")
        next_btn.setToolTip("Next Page (→)")
        next_btn.clicked.connect(self.next_page)
        toolbar_layout.addWidget(next_btn)

        # Enhanced page navigation with jump-to-page
        from PyQt5.QtWidgets import QLineEdit, QCompleter
        from PyQt5.QtCore import QStringListModel
        
        # Page info with clickable jump-to-page
        self.page_info = QPushButton("No document")
        self.page_info.setToolTip("Click to jump to page")
        self.page_info.setStyleSheet("""
            QPushButton {
                color: #666666;
                font-size: 11px;
                padding: 4px 8px;
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border: 1px solid #E0E0E0;
            }
        """)
        self.page_info.clicked.connect(self.show_jump_to_page)
        toolbar_layout.addWidget(self.page_info)
        
        # Hidden jump-to-page input (will be shown when needed)
        self.jump_input = QLineEdit()
        self.jump_input.setPlaceholderText("Page number...")
        self.jump_input.setMaximumWidth(100)
        self.jump_input.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 2px solid #0078D4;
                border-radius: 3px;
                font-size: 11px;
            }
        """)
        self.jump_input.returnPressed.connect(self.jump_to_page)
        self.jump_input.hide()
        toolbar_layout.addWidget(self.jump_input)

        toolbar_layout.addStretch()

        # Enhanced zoom controls with percentage display
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setToolTip("Zoom Out (Ctrl+-)")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)

        # Zoom level display (clickable for presets)
        self.zoom_info = QPushButton("100%")
        self.zoom_info.setToolTip("Click for zoom presets")
        self.zoom_info.setStyleSheet("""
            QPushButton {
                color: #666666;
                font-size: 11px;
                padding: 4px 8px;
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                min-width: 35px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border: 1px solid #E0E0E0;
            }
        """)
        self.zoom_info.clicked.connect(self.show_zoom_presets)
        toolbar_layout.addWidget(self.zoom_info)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setToolTip("Zoom In (Ctrl++)")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)

        # Enhanced fit options
        fit_btn = QPushButton("Fit")
        fit_btn.setToolTip("Fit options (Ctrl+0)")
        fit_btn.clicked.connect(self.show_fit_options)
        toolbar_layout.addWidget(fit_btn)

        # Add separator before search
        sep2 = QWidget()
        sep2.setFixedSize(1, 25)
        sep2.setStyleSheet("background-color: #D5D5D5;")
        toolbar_layout.addWidget(sep2)

        # View mode toggle
        self.view_mode_btn = QPushButton("📄")
        self.view_mode_btn.setToolTip("Switch to Continuous View (Ctrl+M)")
        self.view_mode_btn.clicked.connect(self.toggle_view_mode)
        toolbar_layout.addWidget(self.view_mode_btn)

        # Search functionality
        search_btn = QPushButton("🔍")
        search_btn.setToolTip("Search in document (Ctrl+F)")
        search_btn.clicked.connect(self.toggle_search)
        toolbar_layout.addWidget(search_btn)

        # Hidden search input (will be shown when needed)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text...")
        self.search_input.setMaximumWidth(150)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 4px 8px;
                border: 2px solid #0078D4;
                border-radius: 3px;
                font-size: 11px;
            }
        """)
        self.search_input.textChanged.connect(self.search_text)
        self.search_input.returnPressed.connect(self.find_next)
        self.search_input.hide()
        toolbar_layout.addWidget(self.search_input)

        # Search navigation buttons (hidden initially)
        self.search_prev_btn = QPushButton("◀")
        self.search_prev_btn.setToolTip("Previous match (Shift+F3)")
        self.search_prev_btn.clicked.connect(self.find_previous)
        self.search_prev_btn.hide()
        toolbar_layout.addWidget(self.search_prev_btn)

        self.search_next_btn = QPushButton("▶")
        self.search_next_btn.setToolTip("Next match (F3)")
        self.search_next_btn.clicked.connect(self.find_next)
        self.search_next_btn.hide()
        toolbar_layout.addWidget(self.search_next_btn)

        self.search_close_btn = QPushButton("✕")
        self.search_close_btn.setToolTip("Close search (Esc)")
        self.search_close_btn.clicked.connect(self.close_search)
        self.search_close_btn.hide()
        toolbar_layout.addWidget(self.search_close_btn)

        # Ultra-minimal button styling
        button_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 6px 8px;
                margin: 1px;
                color: #555555;
                font-size: 12px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border: 1px solid #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """
        
        for button in toolbar.findChildren(QPushButton):
            button.setStyleSheet(button_style)

        parent_layout.addWidget(toolbar)

    def create_annotation_toolbar(self, parent_layout):
        """Create annotation toolbar if annotation system is available"""
        if not self.annotation_manager:
            return
        
        try:
            from annotations.ui.annotation_toolbar import AnnotationToolbar
            
            self.annotation_toolbar = AnnotationToolbar()
            self.annotation_toolbar.setFixedHeight(40)
            
            # Connect signals
            self.annotation_toolbar.add_bookmark_requested.connect(self.toggle_bookmark)
            self.annotation_toolbar.toggle_bookmarks_panel.connect(self.toggle_bookmark_sidebar)
            self.annotation_toolbar.highlight_mode_toggled.connect(self.set_highlight_mode)
            self.annotation_toolbar.highlight_color_changed.connect(self.set_highlight_color)
            self.annotation_toolbar.add_note_requested.connect(self.add_note)
            self.annotation_toolbar.toggle_annotations_panel.connect(self.toggle_highlight_panel)
            self.annotation_toolbar.toggle_notes_panel.connect(self.toggle_note_panel)
            
            # Initially disable until document is loaded
            self.annotation_toolbar.enable_actions(False)
            
            parent_layout.addWidget(self.annotation_toolbar)
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info("Annotation toolbar created")
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to create annotation toolbar: {e}")

    def create_bookmark_sidebar(self, parent_layout):
        """Create bookmark sidebar if annotation system is available"""
        if not self.annotation_manager:
            return
        
        try:
            from annotations.ui.bookmark_ui import BookmarkSidebar
            
            self.bookmark_sidebar = BookmarkSidebar(self.annotation_manager.bookmark_manager)
            self.bookmark_sidebar.setFixedWidth(250)
            self.bookmark_sidebar.setVisible(False)  # Initially hidden
            
            # Connect signals
            self.bookmark_sidebar.bookmark_selected.connect(self.navigate_to_bookmark)
            self.bookmark_sidebar.bookmark_edited.connect(self.edit_bookmark)
            self.bookmark_sidebar.bookmark_deleted.connect(self.delete_bookmark)
            
            parent_layout.addWidget(self.bookmark_sidebar)
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info("Bookmark sidebar created")
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to create bookmark sidebar: {e}")

    def update_page_info(self, current_page=None, total_pages=None):
        """Update the enhanced page info display."""
        if hasattr(self, 'page_info'):
            if current_page and total_pages:
                self.page_info.setText(f"{current_page}/{total_pages}")
                self.page_info.setToolTip(f"Page {current_page} of {total_pages} - Click to jump to page")
            else:
                self.page_info.setText("No document")
                self.page_info.setToolTip("No document loaded")

    def update_zoom_info(self, zoom_level):
        """Update the zoom level display."""
        if hasattr(self, 'zoom_info'):
            percentage = int(zoom_level * 100)
            self.zoom_info.setText(f"{percentage}%")
            self.zoom_info.setToolTip(f"Zoom: {percentage}% - Click for presets")

    def show_jump_to_page(self):
        """Show the jump-to-page input."""
        if self.document_viewer and self.document_viewer.get_total_pages() > 0:
            self.page_info.hide()
            self.jump_input.show()
            self.jump_input.setFocus()
            self.jump_input.selectAll()

    def jump_to_page(self):
        """Jump to the specified page."""
        try:
            page_text = self.jump_input.text().strip()
            if page_text:
                page_num = int(page_text)
                if self.document_viewer:
                    total_pages = self.document_viewer.get_total_pages()
                    if 1 <= page_num <= total_pages:
                        self.document_viewer.jump_to_page(page_num - 1)  # Convert to 0-based
                        self.update_page_info_display()
                        self.update_note_display()
        except ValueError:
            pass  # Invalid input, ignore
        finally:
            self.jump_input.hide()
            self.page_info.show()
            self.jump_input.clear()

    def show_zoom_presets(self):
        """Show zoom preset options."""
        from PyQt5.QtWidgets import QMenu
        
        if not self.document_viewer:
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 12px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
        """)
        
        # Add zoom presets
        presets = [
            ("50%", 0.5),
            ("75%", 0.75),
            ("100%", 1.0),
            ("125%", 1.25),
            ("150%", 1.5),
            ("200%", 2.0),
        ]
        
        for text, zoom in presets:
            action = menu.addAction(text)
            action.triggered.connect(lambda checked, z=zoom: self.set_zoom_level(z))
        
        # Show menu at button position
        menu.exec_(self.zoom_info.mapToGlobal(self.zoom_info.rect().bottomLeft()))

    def show_fit_options(self):
        """Show fit options menu."""
        from PyQt5.QtWidgets import QMenu
        
        if not self.document_viewer:
            return
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 12px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
        """)
        
        # Add fit options
        fit_window = menu.addAction("Fit to Window")
        fit_window.triggered.connect(self.fit_to_window)
        
        fit_width = menu.addAction("Fit to Width")
        fit_width.triggered.connect(self.fit_to_width)
        
        fit_height = menu.addAction("Fit to Height")
        fit_height.triggered.connect(self.fit_to_height)
        
        # Show menu at button position
        menu.exec_(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    def set_zoom_level(self, zoom_level):
        """Set specific zoom level."""
        if self.document_viewer:
            self.document_viewer.set_zoom_level(zoom_level)
            self.update_zoom_info(zoom_level)

    def fit_to_width(self):
        """Fit document to window width."""
        if self.document_viewer:
            zoom_level = self.document_viewer.fit_to_width()
            self.update_zoom_info(zoom_level)

    def fit_to_height(self):
        """Fit document to window height."""
        if self.document_viewer:
            zoom_level = self.document_viewer.fit_to_height()
            self.update_zoom_info(zoom_level)

    def toggle_search(self):
        """Toggle search functionality."""
        # Show the advanced search page
        self.show_search()

    def show_search(self):
        """Show search interface."""
        self.search_input.show()
        self.search_prev_btn.show()
        self.search_next_btn.show()
        self.search_close_btn.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def close_search(self):
        """Close search interface."""
        self.search_input.hide()
        self.search_prev_btn.hide()
        self.search_next_btn.hide()
        self.search_close_btn.hide()
        self.search_input.clear()
        
        # Clear search highlights
        if self.document_viewer:
            self.document_viewer.clear_search_highlights()

    def search_text(self, text):
        """Search for text in the document."""
        if self.document_viewer and text.strip():
            self.document_viewer.search_text(text.strip())

    def find_next(self):
        """Find next search match."""
        if self.document_viewer:
            self.document_viewer.find_next()

    def find_previous(self):
        """Find previous search match."""
        if self.document_viewer:
            self.document_viewer.find_previous()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def handle_escape(self):
        """Handle escape key - close search or exit fullscreen."""
        if self.search_input.isVisible():
            self.close_search()
        elif self.isFullScreen():
            self.showNormal()

    def toggle_view_mode(self):
        """Toggle between page mode and continuous mode."""
        if not self.document_viewer or not self.document_viewer.current_document:
            return
            
        current_mode = self.document_viewer.get_view_mode()
        if current_mode == "page":
            # Switch to continuous mode
            self.document_viewer.set_view_mode("continuous")
            self.view_mode_btn.setText("📜")
            self.view_mode_btn.setToolTip("Switch to Page View (Ctrl+M)")
        else:
            # Switch to page mode
            self.document_viewer.set_view_mode("page")
            self.view_mode_btn.setText("📄")
            self.view_mode_btn.setToolTip("Switch to Continuous View (Ctrl+M)")
            
        # Save preference
        try:
            from utils.settings import set_setting
            set_setting("view_mode", self.document_viewer.get_view_mode())
        except:
            pass

    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are supported file types
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.pdf', '.epub', '.mobi')):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(('.pdf', '.epub', '.mobi')):
                        self.load_document(file_path)
                        event.acceptProposedAction()
                        return
        event.ignore()

    def setup_shortcuts(self):
        """Setup comprehensive keyboard shortcuts for professional use."""
        # File operations
        open_action = QAction(self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        self.addAction(open_action)

        # Home shortcut
        home_action = QAction(self)
        home_action.setShortcut(QKeySequence(Qt.ALT | Qt.Key_H))
        home_action.triggered.connect(self.show_welcome)
        self.addAction(home_action)

        # Arrow keys
        left_action = QAction(self)
        left_action.setShortcut(Qt.Key_Left)
        left_action.triggered.connect(self.previous_page)
        self.addAction(left_action)

        right_action = QAction(self)
        right_action.setShortcut(Qt.Key_Right)
        right_action.triggered.connect(self.next_page)
        self.addAction(right_action)

        # Page Up/Down
        page_up_action = QAction(self)
        page_up_action.setShortcut(Qt.Key_PageUp)
        page_up_action.triggered.connect(self.previous_page)
        self.addAction(page_up_action)

        page_down_action = QAction(self)
        page_down_action.setShortcut(Qt.Key_PageDown)
        page_down_action.triggered.connect(self.next_page)
        self.addAction(page_down_action)

        # Zoom shortcuts
        zoom_in_action = QAction(self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        self.addAction(zoom_in_action)

        zoom_out_action = QAction(self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        self.addAction(zoom_out_action)

        # Fit to window
        fit_action = QAction(self)
        fit_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_0))
        fit_action.triggered.connect(self.fit_to_window)
        self.addAction(fit_action)

        # Search shortcuts
        search_action = QAction(self)
        search_action.setShortcut(QKeySequence.Find)
        search_action.triggered.connect(self.toggle_search)
        self.addAction(search_action)

        find_next_action = QAction(self)
        find_next_action.setShortcut(Qt.Key_F3)
        find_next_action.triggered.connect(self.find_next)
        self.addAction(find_next_action)

        find_prev_action = QAction(self)
        find_prev_action.setShortcut(QKeySequence(Qt.SHIFT | Qt.Key_F3))
        find_prev_action.triggered.connect(self.find_previous)
        self.addAction(find_prev_action)

        # Full screen
        fullscreen_action = QAction(self)
        fullscreen_action.setShortcut(Qt.Key_F11)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # View mode toggle
        view_mode_action = QAction(self)
        view_mode_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_M))
        view_mode_action.triggered.connect(self.toggle_view_mode)
        self.addAction(view_mode_action)

        # Escape key to close search or exit fullscreen
        escape_action = QAction(self)
        escape_action.setShortcut(Qt.Key_Escape)
        escape_action.triggered.connect(self.handle_escape)
        self.addAction(escape_action)

    def ensure_document_viewer(self):
        """Ensure document viewer is created when needed."""
        if self.document_viewer is None:
            try:
                from utils.logger import setup_logging
                logger = setup_logging()
                logger.info("Creating DocumentViewer...")
            except:
                pass
            from ui.document_viewer import DocumentViewer
            self.document_viewer = DocumentViewer()
            self.document_viewer_layout.addWidget(self.document_viewer)
            
            # Initialize note renderer overlay
            self.init_note_renderer()
            
            try:
                logger.info("DocumentViewer created successfully")
            except:
                pass

    def show_welcome(self):
        """Show the welcome page."""
        self.stacked_widget.setCurrentIndex(0)
    
    # Bookmark-related methods
    def toggle_bookmark(self):
        """Toggle bookmark on current page"""
        if not self.annotation_manager or not self.current_document:
            return
        
        try:
            current_page = self.get_current_page()
            if current_page is None:
                return
            
            # Check if bookmark exists
            existing_bookmark = self.annotation_manager.bookmark_manager.get_bookmark_for_page(
                self.current_document.file_path, current_page
            )
            
            if existing_bookmark:
                # Remove existing bookmark
                success = self.annotation_manager.delete_bookmark(existing_bookmark.id)
                if success:
                    self.update_bookmark_indicators()
                    self.update_annotation_toolbar()
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Removed bookmark from page {current_page}")
            else:
                # Add new bookmark
                self.show_add_bookmark_dialog(current_page)
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to toggle bookmark: {e}")
    
    def show_add_bookmark_dialog(self, page_number: int):
        """Show dialog to add a new bookmark"""
        if not self.annotation_manager:
            return
        
        try:
            from annotations.ui.bookmark_ui import BookmarkDialog
            
            categories = self.annotation_manager.get_categories()
            dialog = BookmarkDialog(categories=categories, parent=self)
            
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_bookmark_data()
                
                bookmark = self.annotation_manager.create_bookmark(
                    document_path=self.current_document.file_path,
                    page_number=page_number,
                    title=data['title'],
                    description=data['description'],
                    category=data['category']
                )
                
                if bookmark:
                    self.update_bookmark_indicators()
                    self.update_annotation_toolbar()
                    if self.bookmark_sidebar:
                        self.bookmark_sidebar.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Added bookmark: {bookmark.title}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to show add bookmark dialog: {e}")
    
    def edit_bookmark(self, bookmark_id: str):
        """Edit an existing bookmark"""
        if not self.annotation_manager:
            return
        
        try:
            bookmark = self.annotation_manager.get_annotation_by_id(bookmark_id)
            if not bookmark:
                return
            
            from annotations.ui.bookmark_ui import BookmarkDialog
            
            categories = self.annotation_manager.get_categories()
            dialog = BookmarkDialog(bookmark=bookmark, categories=categories, parent=self)
            
            if dialog.exec_() == dialog.Accepted:
                success = self.annotation_manager.update_bookmark(bookmark)
                if success:
                    self.update_bookmark_indicators()
                    if self.bookmark_sidebar:
                        self.bookmark_sidebar.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Updated bookmark: {bookmark.title}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to edit bookmark: {e}")
    
    def delete_bookmark(self, bookmark_id: str):
        """Delete a bookmark with confirmation"""
        if not self.annotation_manager:
            return
        
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            bookmark = self.annotation_manager.get_annotation_by_id(bookmark_id)
            if not bookmark:
                return
            
            reply = QMessageBox.question(
                self, "Delete Bookmark",
                f"Are you sure you want to delete the bookmark '{bookmark.title}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.annotation_manager.delete_bookmark(bookmark_id)
                if success:
                    self.update_bookmark_indicators()
                    self.update_annotation_toolbar()
                    if self.bookmark_sidebar:
                        self.bookmark_sidebar.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Deleted bookmark: {bookmark.title}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to delete bookmark: {e}")
    
    def navigate_to_bookmark(self, document_path: str, page_number: int):
        """Navigate to a bookmarked page"""
        try:
            if document_path != self.current_document.file_path:
                # Load different document
                self.load_document(document_path)
            
            # Navigate to page
            if self.document_viewer and hasattr(self.document_viewer, 'go_to_page'):
                self.document_viewer.go_to_page(page_number)
                self.update_page_info_display()
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to navigate to bookmark: {e}")
    
    def toggle_bookmark_sidebar(self):
        """Toggle bookmark sidebar visibility"""
        if self.bookmark_sidebar:
            visible = not self.bookmark_sidebar.isVisible()
            self.bookmark_sidebar.setVisible(visible)
            
            if self.annotation_toolbar:
                self.annotation_toolbar.set_panel_visibility("bookmarks", visible)
    
    def toggle_highlight_panel(self):
        """Toggle highlight panel visibility"""
        if not hasattr(self, 'highlight_panel'):
            self.create_highlight_panel()
        
        if self.highlight_panel:
            visible = not self.highlight_panel.isVisible()
            self.highlight_panel.setVisible(visible)
            
            if self.annotation_toolbar:
                self.annotation_toolbar.set_panel_visibility("annotations", visible)
    
    def update_bookmark_indicators(self):
        """Update bookmark indicators in document viewer"""
        # This will be implemented when we integrate with document viewer rendering
        pass
    
    def update_annotation_toolbar(self):
        """Update annotation toolbar state"""
        if not self.annotation_toolbar or not self.current_document:
            return
        
        try:
            current_page = self.get_current_page()
            if current_page is not None:
                bookmark_exists = self.annotation_manager.bookmark_manager.bookmark_exists(
                    self.current_document.file_path, current_page
                )
                self.annotation_toolbar.set_bookmark_exists(bookmark_exists)
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to update annotation toolbar: {e}")
    
    def get_current_page(self) -> int:
        """Get current page number"""
        if self.document_viewer and hasattr(self.document_viewer, 'get_current_page'):
            return self.document_viewer.get_current_page()
        return 1
    
    # Highlight and note functionality
    def set_highlight_mode(self, enabled: bool):
        """Set highlight mode for text selection"""
        if not hasattr(self, 'highlight_mode_manager'):
            self.init_highlight_mode_manager()
        
        if self.highlight_mode_manager:
            self.highlight_mode_manager.enable_highlight_mode(enabled)
            
            # Update cursor and UI feedback
            if enabled:
                self.statusBar().showMessage("Highlight mode enabled - Select text to highlight", 3000)
            else:
                self.statusBar().showMessage("Highlight mode disabled", 2000)
    
    def set_highlight_color(self, color: str):
        """Set highlight color for new highlights"""
        if not hasattr(self, 'highlight_mode_manager'):
            self.init_highlight_mode_manager()
        
        if self.highlight_mode_manager:
            self.highlight_mode_manager.set_highlight_color(color)
    
    def add_note(self):
        """Add note at current cursor position or enable note mode"""
        if not self.annotation_manager:
            return
        
        try:
            # Enable note placement mode
            if not hasattr(self, 'note_placement_manager'):
                self.init_note_placement_manager()
            
            if self.note_placement_manager:
                self.note_placement_manager.enable_note_mode(True)
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to add note: {e}")
    
    def init_note_placement_manager(self):
        """Initialize note placement manager"""
        try:
            from annotations.ui.note_positioning import NotePlacementManager
            self.note_placement_manager = NotePlacementManager(self)
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to initialize note placement manager: {e}")
            self.note_placement_manager = None
    
    def init_note_renderer(self):
        """Initialize note renderer overlay"""
        if not self.annotation_manager or not self.document_viewer:
            return
        
        try:
            from annotations.ui.note_positioning import NoteRenderer
            
            self.note_renderer = NoteRenderer(self.document_viewer)
            self.note_renderer.note_clicked.connect(self.on_note_clicked)
            self.note_renderer.note_hovered.connect(self.on_note_hovered)
            
            # Position the renderer as an overlay
            self.note_renderer.resize(self.document_viewer.size())
            self.note_renderer.show()
            self.note_renderer.raise_()
            
            # Connect to document viewer resize events
            if hasattr(self.document_viewer, 'resizeEvent'):
                original_resize = self.document_viewer.resizeEvent
                def new_resize_event(event):
                    original_resize(event)
                    if hasattr(self, 'note_renderer') and self.note_renderer:
                        self.note_renderer.resize(event.size())
                self.document_viewer.resizeEvent = new_resize_event
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info("Note renderer initialized")
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to initialize note renderer: {e}")
            self.note_renderer = None
    
    def on_note_clicked(self, note_id: str):
        """Handle note click events"""
        try:
            from annotations.ui.note_ui import NoteTooltip
            
            note = self.annotation_manager.get_annotation_by_id(note_id)
            if note:
                # Show note tooltip or dialog
                tooltip = NoteTooltip(note, self)
                
                # Position tooltip near cursor
                cursor_pos = self.mapFromGlobal(self.cursor().pos())
                tooltip.move(cursor_pos.x() + 10, cursor_pos.y() + 10)
                tooltip.show()
                
                # Auto-hide after 5 seconds
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(5000, tooltip.hide)
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to handle note click: {e}")
    
    def on_note_hovered(self, note_id: str):
        """Handle note hover events"""
        try:
            note = self.annotation_manager.get_annotation_by_id(note_id)
            if note:
                # Update status bar with note preview
                preview = note.plain_text[:100]
                if len(note.plain_text) > 100:
                    preview += "..."
                self.statusBar().showMessage(f"Note: {preview}", 3000)
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to handle note hover: {e}")
    
    def show_add_note_dialog(self, position: Point):
        """Show dialog to add a new note"""
        if not self.annotation_manager:
            return
        
        try:
            from annotations.ui.note_ui import NoteDialog
            
            categories = self.annotation_manager.get_categories()
            dialog = NoteDialog(categories=categories, position=position, parent=self)
            
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_note_data()
                
                current_page = self.get_current_page()
                if current_page is None:
                    return
                
                note = self.annotation_manager.create_note(
                    document_path=self.current_document.file_path,
                    page_number=current_page,
                    position=position,
                    content=data['content'],
                    plain_text=data['plain_text'],
                    category=data['category']
                )
                
                if note:
                    self.update_note_display()
                    if hasattr(self, 'note_panel') and self.note_panel:
                        self.note_panel.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Added note: {note.plain_text[:50]}...")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to show add note dialog: {e}")
    
    def edit_note(self, note_id: str):
        """Edit an existing note"""
        if not self.annotation_manager:
            return
        
        try:
            note = self.annotation_manager.get_annotation_by_id(note_id)
            if not note:
                return
            
            from annotations.ui.note_ui import NoteDialog
            
            categories = self.annotation_manager.get_categories()
            dialog = NoteDialog(note=note, categories=categories, parent=self)
            
            if dialog.exec_() == dialog.Accepted:
                success = self.annotation_manager.update_note(note)
                if success:
                    self.update_note_display()
                    if hasattr(self, 'note_panel') and self.note_panel:
                        self.note_panel.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Updated note: {note.id}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to edit note: {e}")
    
    def delete_note(self, note_id: str):
        """Delete a note with confirmation"""
        if not self.annotation_manager:
            return
        
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            note = self.annotation_manager.get_annotation_by_id(note_id)
            if not note:
                return
            
            reply = QMessageBox.question(
                self, "Delete Note",
                f"Are you sure you want to delete this note?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.annotation_manager.delete_note(note_id)
                if success:
                    self.update_note_display()
                    if hasattr(self, 'note_panel') and self.note_panel:
                        self.note_panel.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Deleted note: {note_id}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to delete note: {e}")
    
    def reply_to_note(self, parent_note_id: str):
        """Reply to an existing note"""
        if not self.annotation_manager:
            return
        
        try:
            parent_note = self.annotation_manager.get_annotation_by_id(parent_note_id)
            if not parent_note:
                return
            
            from annotations.ui.note_ui import NoteDialog
            
            categories = self.annotation_manager.get_categories()
            dialog = NoteDialog(categories=categories, position=parent_note.position, parent=self)
            dialog.setWindowTitle("Reply to Note")
            
            if dialog.exec_() == dialog.Accepted:
                data = dialog.get_note_data()
                
                reply_note = self.annotation_manager.note_manager.create_reply(
                    parent_note_id=parent_note_id,
                    content=data['content'],
                    plain_text=data['plain_text'],
                    category=data['category']
                )
                
                if reply_note:
                    self.update_note_display()
                    if hasattr(self, 'note_panel') and self.note_panel:
                        self.note_panel.refresh()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Added reply to note: {parent_note_id}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to reply to note: {e}")
    
    def navigate_to_note(self, document_path: str, page_number: int):
        """Navigate to a note's page"""
        try:
            if document_path != self.current_document.file_path:
                # Load different document
                self.load_document(document_path)
            
            # Navigate to page
            if self.document_viewer and hasattr(self.document_viewer, 'go_to_page'):
                self.document_viewer.go_to_page(page_number)
                self.update_page_info_display()
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to navigate to note: {e}")
    
    def update_note_display(self):
        """Update note display in document viewer"""
        if not self.annotation_manager or not self.current_document:
            return
        
        try:
            current_page = self.get_current_page()
            if current_page is None:
                return
            
            # Get notes for current page
            notes = self.annotation_manager.get_notes(
                self.current_document.file_path, current_page
            )
            
            # Update note renderer if available
            if hasattr(self, 'note_renderer') and self.note_renderer:
                self.note_renderer.set_notes(notes)
            
            # Update note placement manager if available
            if hasattr(self, 'note_placement_manager') and self.note_placement_manager:
                self.note_placement_manager.update_note_display(notes)
            
            # Update note panel if available
            if hasattr(self, 'note_panel') and self.note_panel:
                self.note_panel.refresh()
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to update note display: {e}")
    
    def create_note_panel(self):
        """Create note management panel"""
        if not self.annotation_manager:
            return
        
        try:
            from annotations.ui.note_ui import NotePanel
            
            self.note_panel = NotePanel(self.annotation_manager.note_manager)
            self.note_panel.setFixedWidth(350)
            self.note_panel.setVisible(False)  # Initially hidden
            
            # Connect signals
            self.note_panel.note_selected.connect(self.navigate_to_note)
            self.note_panel.note_edited.connect(self.edit_note)
            self.note_panel.note_deleted.connect(self.delete_note)
            self.note_panel.note_replied.connect(self.reply_to_note)
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info("Note panel created")
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to create note panel: {e}")
    
    def toggle_note_panel(self):
        """Toggle note panel visibility"""
        if not hasattr(self, 'note_panel'):
            self.create_note_panel()
        
        if self.note_panel:
            visible = not self.note_panel.isVisible()
            self.note_panel.setVisible(visible)
            
            if self.annotation_toolbar:
                self.annotation_toolbar.set_panel_visibility("notes", visible)
    
    def init_highlight_mode_manager(self):
        """Initialize highlight mode manager"""
        try:
            from annotations.ui.text_selection import HighlightModeManager
            self.highlight_mode_manager = HighlightModeManager(self)
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to initialize highlight mode manager: {e}")
            self.highlight_mode_manager = None
    
    def update_highlight_display(self):
        """Update highlight display in document viewer"""
        if not self.annotation_manager or not self.current_document:
            return
        
        try:
            current_page = self.get_current_page()
            if current_page is None:
                return
            
            # Get highlights for current page
            highlights = self.annotation_manager.get_highlights(
                self.current_document.file_path, current_page
            )
            
            # Update highlight renderer if available
            if hasattr(self, 'highlight_renderer') and self.highlight_renderer:
                self.highlight_renderer.set_highlights(highlights)
            
            # Update highlight panel if available
            if hasattr(self, 'highlight_panel') and self.highlight_panel:
                self.highlight_panel.refresh()
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to update highlight display: {e}")
    
    def create_highlight_panel(self):
        """Create highlight management panel"""
        if not self.annotation_manager:
            return
        
        try:
            from annotations.ui.highlight_ui import HighlightPanel
            
            self.highlight_panel = HighlightPanel(self.annotation_manager.highlight_manager)
            self.highlight_panel.setFixedWidth(300)
            self.highlight_panel.setVisible(False)  # Initially hidden
            
            # Connect signals
            self.highlight_panel.highlight_selected.connect(self.navigate_to_highlight)
            self.highlight_panel.highlight_edited.connect(self.edit_highlight)
            self.highlight_panel.highlight_deleted.connect(self.delete_highlight)
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info("Highlight panel created")
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to create highlight panel: {e}")
    
    def navigate_to_highlight(self, document_path: str, page_number: int):
        """Navigate to a highlighted page"""
        try:
            if document_path != self.current_document.file_path:
                # Load different document
                self.load_document(document_path)
            
            # Navigate to page
            if self.document_viewer and hasattr(self.document_viewer, 'go_to_page'):
                self.document_viewer.go_to_page(page_number)
                self.update_page_info_display()
                
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to navigate to highlight: {e}")
    
    def edit_highlight(self, highlight_id: str):
        """Edit an existing highlight"""
        if not self.annotation_manager:
            return
        
        try:
            highlight = self.annotation_manager.get_annotation_by_id(highlight_id)
            if not highlight:
                return
            
            from annotations.ui.highlight_ui import HighlightDialog
            
            categories = self.annotation_manager.get_categories()
            dialog = HighlightDialog(highlight=highlight, categories=categories, parent=self)
            
            if dialog.exec_() == dialog.Accepted:
                success = self.annotation_manager.update_highlight(highlight)
                if success:
                    self.update_highlight_display()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Updated highlight: {highlight.id}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to edit highlight: {e}")
    
    def delete_highlight(self, highlight_id: str):
        """Delete a highlight with confirmation"""
        if not self.annotation_manager:
            return
        
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            highlight = self.annotation_manager.get_annotation_by_id(highlight_id)
            if not highlight:
                return
            
            reply = QMessageBox.question(
                self, "Delete Highlight",
                f"Are you sure you want to delete this highlight?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.annotation_manager.delete_highlight(highlight_id)
                if success:
                    self.update_highlight_display()
                    
                    import logging
                    logger = logging.getLogger("ebook_reader")
                    logger.info(f"Deleted highlight: {highlight_id}")
                    
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to delete highlight: {e}")
    
    def init_document_annotations(self, file_path: str):
        """Initialize annotations for the loaded document"""
        if not self.annotation_manager:
            return
        
        try:
            # Enable annotation toolbar
            if self.annotation_toolbar:
                self.annotation_toolbar.enable_actions(True)
                self.update_annotation_toolbar()
            
            # Load bookmarks in sidebar
            if self.bookmark_sidebar:
                self.bookmark_sidebar.set_document(file_path)
            
            # Update bookmark indicators
            self.update_bookmark_indicators()
            
            # Update highlight display
            self.update_highlight_display()
            
            # Create highlight panel if not exists
            if not hasattr(self, 'highlight_panel'):
                self.create_highlight_panel()
            
            # Set document in highlight panel
            if hasattr(self, 'highlight_panel') and self.highlight_panel:
                self.highlight_panel.set_document(file_path)
            
            # Create note panel if not exists
            if not hasattr(self, 'note_panel'):
                self.create_note_panel()
            
            # Set document in note panel
            if hasattr(self, 'note_panel') and self.note_panel:
                self.note_panel.set_document(file_path)
            
            # Update note display
            self.update_note_display()
            
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info(f"Initialized annotations for document: {file_path}")
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to initialize document annotations: {e}")
    
    def show_search(self):
        """Show the search page."""
        if self.search_engine and hasattr(self, 'search_widget'):
            # Find search widget index
            for i in range(self.stacked_widget.count()):
                if self.stacked_widget.widget(i) == self.search_widget:
                    self.stacked_widget.setCurrentIndex(i)
                    break
    
    def open_search_result(self, document_path: str, page_number: int):
        """Open a document from search results at specific page."""
        try:
            # Load the document
            self.load_document(document_path)
            
            # Navigate to the specific page
            if self.document_viewer and hasattr(self.document_viewer, 'go_to_page'):
                self.document_viewer.go_to_page(page_number)
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to open search result: {e}")
    
    def index_document_async(self, file_path: str):
        """Index document for search in background."""
        if not self.search_indexer:
            return
        
        try:
            from PyQt5.QtCore import QThread, pyqtSignal
            
            class IndexWorker(QThread):
                finished = pyqtSignal(bool, str)
                
                def __init__(self, indexer, file_path):
                    super().__init__()
                    self.indexer = indexer
                    self.file_path = file_path
                
                def run(self):
                    try:
                        success = self.indexer.index_document(self.file_path)
                        self.finished.emit(success, self.file_path)
                    except Exception as e:
                        self.finished.emit(False, str(e))
            
            # Start indexing in background
            self.index_worker = IndexWorker(self.search_indexer, file_path)
            self.index_worker.finished.connect(self.on_indexing_finished)
            self.index_worker.start()
            
        except Exception as e:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.error(f"Failed to start document indexing: {e}")
    
    def on_indexing_finished(self, success: bool, result: str):
        """Handle indexing completion."""
        if success:
            import logging
            logger = logging.getLogger("ebook_reader")
            logger.info(f"Document indexed for search: {result}")
        # Cleanup worker
        if hasattr(self, 'index_worker'):
            self.index_worker.deleteLater()

    def show_document(self):
        """Show the document viewer page."""
        self.stacked_widget.setCurrentIndex(1)

    def open_file(self):
        """Open a document file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported (*.pdf *.epub *.mobi);;PDF Files (*.pdf);;EPUB Files (*.epub);;MOBI Files (*.mobi)"
        )

        if file_path:
            self.load_document(file_path)

    def load_document(self, file_path):
        """Load and display a document."""
        try:
            # Import document manager
            from readers.document_manager import DocumentManager
            from utils.settings import add_recent_book
            
            if not self.document_manager:
                self.document_manager = DocumentManager()

            # Load document
            self.current_document = self.document_manager.load_document(file_path)
            
            if self.current_document:
                # Add to recent books
                add_recent_book(file_path)
                
                # Update welcome widget recent books
                if hasattr(self, 'welcome_widget'):
                    self.welcome_widget.add_recent_book(file_path)
                
                # Index document for search (in background)
                self.index_document_async(file_path)
                
                # Ensure document viewer exists
                self.ensure_document_viewer()
                
                # Load document into viewer
                self.document_viewer.load_document(self.current_document)
                
                # Switch to document view
                self.show_document()
                
                # Update window title and page info
                filename = Path(file_path).name
                self.setWindowTitle(f"Modern EBook Reader - {filename}")
                self.update_page_info_display()
                
                # Initialize zoom info
                self.update_zoom_info(self.document_viewer.zoom_level)
                
                # Initialize annotations for this document
                self.init_document_annotations(file_path)
                
                # Set initial view mode from settings
                try:
                    from utils.settings import get_setting
                    saved_mode = get_setting("view_mode", "page")
                    self.document_viewer.set_view_mode(saved_mode)
                    if saved_mode == "continuous":
                        self.view_mode_btn.setText("📜")
                        self.view_mode_btn.setToolTip("Switch to Page View (Ctrl+M)")
                    else:
                        self.view_mode_btn.setText("📄")
                        self.view_mode_btn.setToolTip("Switch to Continuous View (Ctrl+M)")
                except:
                    pass
                
                try:
                    from utils.logger import setup_logging
                    logger = setup_logging()
                    logger.info("Document loaded successfully: %s", filename)
                except:
                    pass

        except Exception as e:
            try:
                from utils.logger import setup_logging
                logger = setup_logging()
                logger.exception("Error loading document: %s", e)
            except:
                pass
            # TODO: Show error message to user

    def previous_page(self):
        """Navigate to previous page."""
        if self.document_viewer and self.document_viewer.previous_page():
            self.update_page_info_display()
            self.update_note_display()

    def next_page(self):
        """Navigate to next page."""
        if self.document_viewer and self.document_viewer.next_page():
            self.update_page_info_display()
            self.update_note_display()

    def update_page_info_display(self):
        """Update page info display after navigation."""
        if self.document_viewer:
            current = self.document_viewer.get_current_page()
            total = self.document_viewer.get_total_pages()
            self.update_page_info(current, total)
            self.update_reading_progress()

    def zoom_in(self):
        """Zoom in."""
        if self.document_viewer:
            zoom_level = self.document_viewer.zoom_in()
            self.update_zoom_info(zoom_level)

    def zoom_out(self):
        """Zoom out."""
        if self.document_viewer:
            zoom_level = self.document_viewer.zoom_out()
            self.update_zoom_info(zoom_level)

    def fit_to_window(self):
        """Fit page to window."""
        if self.document_viewer:
            zoom_level = self.document_viewer.fit_to_window()
            self.update_zoom_info(zoom_level)

    def create_status_bar(self):
        """Create a minimal status bar for reading progress."""
        from PyQt5.QtWidgets import QProgressBar, QLabel
        
        self.status_bar = QWidget()
        self.status_bar.setFixedHeight(25)
        self.status_bar.setStyleSheet("""
            QWidget {
                background-color: #F8F8F8;
                border-top: 1px solid #E5E5E5;
            }
        """)
        
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(15, 4, 15, 4)
        status_layout.setSpacing(10)
        
        # Reading progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #D0D0D0;
                border-radius: 7px;
                background-color: #F0F0F0;
                text-align: center;
                font-size: 10px;
                color: #666666;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 6px;
            }
        """)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        # Document info
        self.doc_info = QLabel("")
        self.doc_info.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 10px;
                background-color: transparent;
            }
        """)
        status_layout.addWidget(self.doc_info)
        
        status_layout.addStretch()
        
        # Reading time estimate
        self.reading_time = QLabel("")
        self.reading_time.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 10px;
                background-color: transparent;
            }
        """)
        status_layout.addWidget(self.reading_time)

    def update_reading_progress(self):
        """Update reading progress indicators."""
        if not self.document_viewer or not self.document_viewer.current_document:
            self.progress_bar.setVisible(False)
            self.doc_info.setText("")
            self.reading_time.setText("")
            return
            
        try:
            current_page = self.document_viewer.get_current_page()
            total_pages = self.document_viewer.get_total_pages()
            
            if total_pages > 0:
                # Update progress bar
                progress = int((current_page / total_pages) * 100)
                self.progress_bar.setValue(progress)
                self.progress_bar.setFormat(f"{progress}%")
                self.progress_bar.setVisible(True)
                
                # Update document info
                try:
                    filename = Path(self.current_document.file_path).name if hasattr(self.current_document, 'file_path') else "Document"
                except:
                    filename = "Document"
                self.doc_info.setText(f"{filename} • {total_pages} pages")
                
                # Estimate reading time (assuming 250 words per minute, 300 words per page)
                remaining_pages = total_pages - current_page
                estimated_minutes = int((remaining_pages * 300) / 250)
                if estimated_minutes > 60:
                    hours = estimated_minutes // 60
                    minutes = estimated_minutes % 60
                    self.reading_time.setText(f"~{hours}h {minutes}m remaining")
                elif estimated_minutes > 0:
                    self.reading_time.setText(f"~{estimated_minutes}m remaining")
                else:
                    self.reading_time.setText("Almost finished!")
            else:
                self.progress_bar.setVisible(False)
                
        except Exception as e:
            logger.exception("Error updating reading progress: %s", e)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.current_document:
            self.current_document = None
        event.accept()
