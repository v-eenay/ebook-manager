"""
Welcome Widget
Displays the welcome screen with file opening options.
"""

from pathlib import Path

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QFrame, QSizePolicy)
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QPixmap, QFont
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QFrame, QSizePolicy)
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPixmap, QFont
    QT_VERSION = 5


class WelcomeWidget(QWidget):
    """Welcome screen widget with modern, minimal design."""
    
    # Signals
    open_file_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the welcome screen UI."""
        layout = QVBoxLayout(self)
        if QT_VERSION == 6:
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container_layout_alignment = Qt.AlignmentFlag.AlignCenter
        else:
            layout.setAlignment(Qt.AlignCenter)
            container_layout_alignment = Qt.AlignCenter

        layout.setSpacing(30)

        # Create main container
        container = QFrame()
        container.setMaximumWidth(600)
        container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
                border-radius: 12px;
                padding: 48px;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(container_layout_alignment)
        container_layout.setSpacing(20)
        
        # App icon
        icon_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if QT_VERSION == 6:
                scaled_pixmap = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            else:
                scaled_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            icon_label.setText("📚")
            icon_label.setStyleSheet("font-size: 48px;")

        if QT_VERSION == 6:
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            icon_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(icon_label)
        
        # App title
        title_label = QLabel("Modern EBook Reader")
        title_font = QFont()
        title_font.setFamily("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
        title_font.setPointSize(28)
        if QT_VERSION == 6:
            title_font.setWeight(QFont.Weight.Bold)
        else:
            title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        if QT_VERSION == 6:
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #000000;
            margin: 16px 0px 24px 0px;
            font-weight: 700;
        """)
        container_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "A clean, minimal ebook reader supporting PDF, EPUB, and MOBI formats.\n\n"
            "• Drag and drop files to open them\n"
            "• Use Ctrl+O to browse for documents\n"
            "• Navigate with arrow keys or mouse wheel\n"
            "• Zoom with Ctrl+mouse wheel"
        )
        if QT_VERSION == 6:
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #1A1A1A;
            font-size: 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-weight: 400;
            line-height: 1.6;
            margin: 16px 0px 32px 0px;
        """)
        container_layout.addWidget(desc_label)
        
        # Open button
        open_button = QPushButton("Open Document")
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 16px 32px;
                font-size: 16px;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:focus {
                outline: 2px solid #1976D2;
                outline-offset: 2px;
            }
        """)
        open_button.clicked.connect(self.open_file_requested.emit)
        container_layout.addWidget(open_button)
        
        # Supported formats
        formats_label = QLabel("Supported formats: PDF, EPUB, MOBI")
        if QT_VERSION == 6:
            formats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            formats_label.setAlignment(Qt.AlignCenter)
        formats_label.setStyleSheet("""
            color: #4A4A4A;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-weight: 500;
            margin-top: 24px;
        """)
        container_layout.addWidget(formats_label)
        
        layout.addWidget(container)
        
        # Set background with better contrast
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
        """)
