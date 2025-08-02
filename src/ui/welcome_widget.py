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
        container.setMaximumWidth(500)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 40px;
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
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        if QT_VERSION == 6:
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #212121; margin: 10px 0;")
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
            color: #666666;
            font-size: 14px;
            line-height: 1.5;
            margin: 10px 0;
        """)
        container_layout.addWidget(desc_label)
        
        # Open button
        open_button = QPushButton("Open Document")
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
            QPushButton:pressed {
                background-color: #2E5BBA;
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
            color: #999999;
            font-size: 12px;
            margin-top: 20px;
        """)
        container_layout.addWidget(formats_label)
        
        layout.addWidget(container)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
            }
        """)
