"""
Welcome Widget
Displays the welcome screen with Fluent Design components.
"""

from pathlib import Path

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QPixmap, QFont
    QT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPixmap, QFont
    QT_VERSION = 5

# Fluent Design System imports
from qfluentwidgets import (
    CardWidget, PrimaryPushButton, TitleLabel, BodyLabel, CaptionLabel,
    FluentIcon as FIF, InfoBar, InfoBarPosition, isDarkTheme,
    StrongBodyLabel, SubtitleLabel, ImageLabel
)


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

        # Create main Fluent Design card container
        container = CardWidget()
        container.setMaximumWidth(600)
        container.setMinimumHeight(400)

        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(container_layout_alignment)
        container_layout.setSpacing(20)
        
        # App icon with Fluent Design
        icon_label = ImageLabel()
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if QT_VERSION == 6:
                scaled_pixmap = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            else:
                scaled_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            # Use Fluent Design book icon as fallback
            icon_label.setText("📚")
            icon_label.setStyleSheet("font-size: 48px;")

        if QT_VERSION == 6:
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            icon_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(icon_label)
        
        # App title with Fluent Design typography
        title_label = TitleLabel("Modern EBook Reader")
        if QT_VERSION == 6:
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Description with Fluent Design typography
        desc_label = BodyLabel(
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
        container_layout.addWidget(desc_label)
        
        # Open button with Fluent Design
        open_button = PrimaryPushButton("Open Document", FIF.FOLDER)
        open_button.setMinimumWidth(160)
        open_button.clicked.connect(self.open_file_requested.emit)
        container_layout.addWidget(open_button)
        
        # Supported formats with Fluent Design
        formats_label = CaptionLabel("Supported formats: PDF, EPUB, MOBI")
        if QT_VERSION == 6:
            formats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            formats_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(formats_label)
        
        layout.addWidget(container)
        
        # Fluent Design background is handled automatically by the framework
