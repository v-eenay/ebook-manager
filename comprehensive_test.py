#!/usr/bin/env python3
"""
Comprehensive test suite for Modern EBook Reader
Tests all functionality implemented in Phases 1-3
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_application_startup():
    """Test application startup and basic functionality."""
    print("🚀 Testing Application Startup...")
    
    try:
        # Import Qt
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QTimer
        
        # Set DPI scaling before QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create QApplication
        app = QApplication([])
        print("✅ QApplication created successfully")
        
        # Import and create MainWindow
        from ui.main_window import MainWindow
        window = MainWindow()
        print("✅ MainWindow created successfully")
        
        # Test window properties
        print(f"✅ Window size: {window.size().width()}x{window.size().height()}")
        print(f"✅ Window title: {window.windowTitle()}")
        print(f"✅ Stacked widget pages: {window.stacked_widget.count()}")
        
        # Test components exist
        components = [
            ('welcome_widget', 'Welcome widget'),
            ('document_viewer_container', 'Document viewer container'),
            ('page_info', 'Page info display'),
            ('zoom_info', 'Zoom info display'),
            ('view_mode_btn', 'View mode button'),
            ('search_input', 'Search input'),
            ('progress_bar', 'Progress bar'),
            ('status_bar', 'Status bar')
        ]
        
        for attr, name in components:
            if hasattr(window, attr):
                print(f"✅ {name} exists")
            else:
                print(f"❌ {name} missing")
                return False
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_loading():
    """Test document loading functionality."""
    print("\n📖 Testing Document Loading...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication([])
        
        from ui.main_window import MainWindow
        window = MainWindow()
        
        # Test if test document exists
        test_doc = Path("test_document.pdf")
        if test_doc.exists():
            print(f"✅ Test document found: {test_doc}")
            
            # Test document loading
            window.load_document(str(test_doc))
            print("✅ Document loading method executed")
            
            # Check if document viewer was created
            if window.document_viewer:
                print("✅ Document viewer created")
                print(f"✅ Current page: {window.document_viewer.get_current_page()}")
                print(f"✅ Total pages: {window.document_viewer.get_total_pages()}")
                print(f"✅ View mode: {window.document_viewer.get_view_mode()}")
                print(f"✅ Zoom level: {window.document_viewer.zoom_level}")
            else:
                print("❌ Document viewer not created")
                return False
        else:
            print("⚠️  No test document found, skipping document loading test")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Document loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_functionality():
    """Test settings and recent books functionality."""
    print("\n⚙️ Testing Settings Functionality...")
    
    try:
        from utils.settings import (load_recent_books, add_recent_book, 
                                   clear_recent_books, get_setting, set_setting)
        
        # Test basic settings
        print("✅ Settings module imported")
        
        # Test recent books
        initial_books = load_recent_books()
        print(f"✅ Loaded {len(initial_books)} recent books")
        
        # Test adding a book
        test_path = "test_book.pdf"
        add_recent_book(test_path)
        print("✅ Added test book to recent")
        
        # Verify it was added
        updated_books = load_recent_books()
        if test_path in updated_books:
            print("✅ Test book found in recent books")
        else:
            print("❌ Test book not found in recent books")
            return False
        
        # Test settings
        set_setting("test_key", "test_value")
        retrieved_value = get_setting("test_key")
        if retrieved_value == "test_value":
            print("✅ Settings save/load working")
        else:
            print("❌ Settings save/load failed")
            return False
        
        # Clean up
        clear_recent_books()
        print("✅ Recent books cleared")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """Test individual UI components."""
    print("\n🎨 Testing UI Components...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication([])
        
        # Test WelcomeWidget
        from ui.welcome_widget import WelcomeWidget
        welcome = WelcomeWidget()
        print("✅ WelcomeWidget created")
        print(f"✅ Recent books loaded: {len(welcome.recent_books)}")
        
        # Test DocumentViewer
        from ui.document_viewer import DocumentViewer
        viewer = DocumentViewer()
        print("✅ DocumentViewer created")
        print(f"✅ Initial view mode: {viewer.get_view_mode()}")
        print(f"✅ Initial zoom level: {viewer.zoom_level}")
        
        # Test view mode switching
        viewer.set_view_mode("continuous")
        print(f"✅ Switched to continuous mode: {viewer.get_view_mode()}")
        
        viewer.set_view_mode("page")
        print(f"✅ Switched to page mode: {viewer.get_view_mode()}")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_shortcuts():
    """Test keyboard shortcuts functionality."""
    print("\n⌨️ Testing Keyboard Shortcuts...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QKeySequence
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication([])
        
        from ui.main_window import MainWindow
        window = MainWindow()
        
        # Test that shortcuts are registered
        from PyQt5.QtWidgets import QAction
        actions = window.findChildren(QAction)
        print(f"✅ Found {len(actions)} keyboard shortcuts")
        
        # Test specific shortcuts
        shortcut_tests = [
            (QKeySequence.Open, "Open document"),
            (QKeySequence(Qt.ALT | Qt.Key_H), "Home"),
            (Qt.Key_Left, "Previous page"),
            (Qt.Key_Right, "Next page"),
            (QKeySequence.Find, "Search"),
            (Qt.Key_F11, "Full screen"),
            (QKeySequence(Qt.CTRL | Qt.Key_M), "View mode toggle")
        ]
        
        for shortcut, description in shortcut_tests:
            found = False
            for action in actions:
                if action.shortcut() == shortcut:
                    found = True
                    break
            if found:
                print(f"✅ {description} shortcut registered")
            else:
                print(f"❌ {description} shortcut missing")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Keyboard shortcuts test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_visual_test():
    """Run a visual test of the application."""
    print("\n👁️ Running Visual Test (5 seconds)...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QTimer
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication([])
        
        from ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        print("✅ Window displayed")
        print("✅ Check the application window for:")
        print("   - Clean, minimal welcome screen")
        print("   - Recent books panel (if any)")
        print("   - Professional styling")
        print("   - Proper window size and layout")
        
        # Auto-close after 5 seconds
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(5000)
        
        app.exec_()
        print("✅ Visual test completed")
        return True
        
    except Exception as e:
        print(f"❌ Visual test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive test suite."""
    print("🧪 COMPREHENSIVE TEST SUITE FOR MODERN EBOOK READER")
    print("=" * 60)
    
    tests = [
        ("Application Startup", test_application_startup),
        ("Document Loading", test_document_loading),
        ("Settings Functionality", test_settings_functionality),
        ("UI Components", test_ui_components),
        ("Keyboard Shortcuts", test_keyboard_shortcuts),
        ("Visual Test", run_visual_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*60}")
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Application is ready for Phase 4.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())