"""
Search UI Components for Modern EBook Reader
Provides search interface and result display
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QPushButton, QListWidget, QListWidgetItem, QLabel,
                            QFrame, QScrollArea, QTextEdit, QCompleter,
                            QProgressBar, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPalette, QTextCharFormat, QTextCursor
from qfluentwidgets import (LineEdit, PushButton, ListWidget, ScrollArea,
                           BodyLabel, CaptionLabel, ProgressBar)
import logging

logger = logging.getLogger("ebook_reader")

class SearchWorker(QThread):
    """Background search worker to avoid UI blocking"""
    
    search_completed = pyqtSignal(list)  # List of SearchResult
    search_progress = pyqtSignal(str)    # Progress message
    
    def __init__(self, search_engine, query, max_results=50):
        super().__init__()
        self.search_engine = search_engine
        self.query = query
        self.max_results = max_results
    
    def run(self):
        """Perform search in background"""
        try:
            self.search_progress.emit("Searching...")
            results = self.search_engine.search(self.query, self.max_results)
            self.search_completed.emit(results)
        except Exception as e:
            logger.error(f"Search worker error: {e}")
            self.search_completed.emit([])

class SearchResultWidget(QFrame):
    """Widget to display a single search result"""
    
    result_clicked = pyqtSignal(str, int)  # document_path, page_number
    
    def __init__(self, search_result):
        super().__init__()
        self.search_result = search_result
        self.init_ui()
    
    def init_ui(self):
        """Initialize the result widget UI"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            SearchResultWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                margin: 2px;
            }
            SearchResultWidget:hover {
                background-color: #f5f5f5;
                border-color: #0078d4;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Document info
        doc_info = QHBoxLayout()
        
        from pathlib import Path
        doc_name = BodyLabel(Path(self.search_result.document_path).name)
        doc_name.setStyleSheet("font-weight: bold; color: #0078d4;")
        doc_info.addWidget(doc_name)
        
        doc_info.addStretch()
        
        page_label = CaptionLabel(f"Page {self.search_result.page_number}")
        page_label.setStyleSheet("color: #666;")
        doc_info.addWidget(page_label)
        
        if self.search_result.relevance_score > 0:
            score_label = CaptionLabel(f"Score: {self.search_result.relevance_score:.2f}")
            score_label.setStyleSheet("color: #666;")
            doc_info.addWidget(score_label)
        
        layout.addLayout(doc_info)
        
        # Text snippet with highlighting
        snippet_widget = QTextEdit()
        snippet_widget.setMaximumHeight(80)
        snippet_widget.setReadOnly(True)
        snippet_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        snippet_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        snippet_widget.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                font-size: 12px;
                color: #333;
            }
        """)
        
        # Set snippet text with highlighting
        self._set_highlighted_text(snippet_widget)
        
        layout.addWidget(snippet_widget)
        
        # Make the whole widget clickable
        self.setCursor(Qt.PointingHandCursor)
    
    def _set_highlighted_text(self, text_widget):
        """Set text with search term highlighted"""
        snippet = self.search_result.text_snippet
        start = self.search_result.match_start
        end = self.search_result.match_end
        
        # Set plain text first
        text_widget.setPlainText(snippet)
        
        # Highlight the match
        if start >= 0 and end > start and end <= len(snippet):
            cursor = text_widget.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            
            # Create highlight format
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(Qt.yellow)
            highlight_format.setForeground(Qt.black)
            
            cursor.setCharFormat(highlight_format)
    
    def mousePressEvent(self, event):
        """Handle click to open document"""
        if event.button() == Qt.LeftButton:
            self.result_clicked.emit(
                self.search_result.document_path,
                self.search_result.page_number
            )
        super().mousePressEvent(event)

class SearchWidget(QWidget):
    """Main search widget with input and results"""
    
    document_requested = pyqtSignal(str, int)  # document_path, page_number
    
    def __init__(self, search_engine):
        super().__init__()
        self.search_engine = search_engine
        self.search_worker = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.init_ui()
        self.setup_completer()
    
    def init_ui(self):
        """Initialize the search UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Search input section
        search_section = self.create_search_section()
        layout.addWidget(search_section)
        
        # Progress bar
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results section
        results_section = self.create_results_section()
        layout.addWidget(results_section)
    
    def create_search_section(self):
        """Create the search input section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title = BodyLabel("Search Documents")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Search input
        input_layout = QHBoxLayout()
        
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText("Enter search terms...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        input_layout.addWidget(self.search_input)
        
        self.search_button = PushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        input_layout.addWidget(self.search_button)
        
        layout.addLayout(input_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        
        self.max_results_label = CaptionLabel("Max results:")
        options_layout.addWidget(self.max_results_label)
        
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(10, 200)
        self.max_results_spin.setValue(50)
        self.max_results_spin.setSuffix(" results")
        options_layout.addWidget(self.max_results_spin)
        
        options_layout.addStretch()
        
        self.clear_button = PushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        options_layout.addWidget(self.clear_button)
        
        layout.addLayout(options_layout)
        
        return section
    
    def create_results_section(self):
        """Create the results display section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Results header
        self.results_header = BodyLabel("Enter search terms to find content")
        self.results_header.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.results_header)
        
        # Results scroll area
        self.results_scroll = ScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setMinimumHeight(400)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(4)
        self.results_layout.addStretch()
        
        self.results_scroll.setWidget(self.results_container)
        layout.addWidget(self.results_scroll)
        
        return section
    
    def setup_completer(self):
        """Setup auto-completion for search input"""
        try:
            history = self.search_engine.get_search_history()
            completer = QCompleter(history)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.search_input.setCompleter(completer)
        except Exception as e:
            logger.error(f"Failed to setup completer: {e}")
    
    def on_search_text_changed(self, text):
        """Handle search text changes with debouncing"""
        if len(text.strip()) >= 3:  # Start searching after 3 characters
            self.search_timer.start(500)  # 500ms delay
        else:
            self.search_timer.stop()
            if not text.strip():
                self.clear_results()
    
    def perform_search(self):
        """Perform the search operation"""
        query = self.search_input.text().strip()
        
        if not query:
            self.clear_results()
            return
        
        # Stop any existing search
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.search_button.setEnabled(False)
        self.results_header.setText("Searching...")
        
        # Start search worker
        max_results = self.max_results_spin.value()
        self.search_worker = SearchWorker(self.search_engine, query, max_results)
        self.search_worker.search_completed.connect(self.on_search_completed)
        self.search_worker.search_progress.connect(self.on_search_progress)
        self.search_worker.start()
    
    def on_search_progress(self, message):
        """Handle search progress updates"""
        self.results_header.setText(message)
    
    def on_search_completed(self, results):
        """Handle search completion"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        
        # Clear previous results
        self.clear_results_widgets()
        
        if not results:
            self.results_header.setText("No results found")
            return
        
        # Update header
        self.results_header.setText(f"Found {len(results)} results")
        
        # Add result widgets
        for result in results:
            result_widget = SearchResultWidget(result)
            result_widget.result_clicked.connect(self.document_requested.emit)
            self.results_layout.insertWidget(self.results_layout.count() - 1, result_widget)
        
        # Update completer with new search
        self.setup_completer()
    
    def clear_results(self):
        """Clear search results"""
        self.search_input.clear()
        self.clear_results_widgets()
        self.results_header.setText("Enter search terms to find content")
    
    def clear_results_widgets(self):
        """Clear result widgets from layout"""
        while self.results_layout.count() > 1:  # Keep the stretch
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def set_search_text(self, text):
        """Set search text programmatically"""
        self.search_input.setText(text)
        self.perform_search()