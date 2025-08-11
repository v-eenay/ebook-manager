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

# Logger will be imported inside methods to avoid early initialization

class MainWindow(QMainWindow):
    """Main window with clean, minimal design focused on document viewing."""

    def __init__(self):
        super().__init__()
        self.current_document = None
        self.document_manager = None
        self.init_ui()
        self.setup_shortcuts()
        self.setup_drag_drop()

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

        # Create document viewer (lazy loading)
        self.document_viewer = None
        self.document_viewer_container = QWidget()
        self.document_viewer_layout = QVBoxLayout(self.document_viewer_container)
        self.document_viewer_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.document_viewer_container)

        self.stacked_widget.addWidget(document_widget)

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
        if not self.document_viewer or not self.document_viewer.current_document:
            return
            
        if self.search_input.isVisible():
            self.close_search()
        else:
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
            try:
                logger.info("DocumentViewer created successfully")
            except:
                pass

    def show_welcome(self):
        """Show the welcome page."""
        self.stacked_widget.setCurrentIndex(0)

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

    def next_page(self):
        """Navigate to next page."""
        if self.document_viewer and self.document_viewer.next_page():
            self.update_page_info_display()

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
