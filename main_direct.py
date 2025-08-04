#!/usr/bin/env python3
"""
Direct main application with Fluent Design - bypassing src structure
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    """Direct main window with Fluent Design components."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Import Fluent Design components inside the method
        from qfluentwidgets import PrimaryPushButton, TitleLabel, BodyLabel, CardWidget
        
        self.setWindowTitle("Modern EBook Reader - Fluent Design")
        self.setMinimumSize(800, 600)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Create title
        title = TitleLabel("Modern EBook Reader")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create card
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add content to card
        text = BodyLabel("Welcome to the Modern EBook Reader with Fluent Design!")
        text.setWordWrap(True)
        card_layout.addWidget(text)
        
        button = PrimaryPushButton("Open Document")
        card_layout.addWidget(button)
        
        layout.addWidget(card)
        layout.addStretch()

def main():
    """Main application entry point."""
    # Create QApplication first
    app = QApplication(sys.argv)
    app.setApplicationName("Modern EBook Reader")
    
    # Initialize Fluent Design theme
    from qfluentwidgets import setTheme, Theme, setThemeColor
    setTheme(Theme.AUTO)
    setThemeColor('#0078D4')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("✅ Fluent Design application started successfully!")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
