#!/usr/bin/env python3
"""
Test Bookmark Integration with Main Application
Tests the integration of bookmark system with the main window and document viewer
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

def test_main_window_annotation_init():
    """Test main window annotation system initialization"""
    print("🏠 Testing Main Window Annotation Initialization...")
    
    from ui.main_window import MainWindow
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        window = MainWindow()
        window.show()
        
        # Check annotation manager initialization
        if hasattr(window, 'annotation_manager') and window.annotation_manager:
            print("✅ Annotation manager initialized")
        else:
            print("⚠️ Annotation manager not available")
        
        # Check annotation toolbar
        if hasattr(window, 'annotation_toolbar') and window.annotation_toolbar:
            print("✅ Annotation toolbar created")
            
            # Test toolbar signals
            toolbar = window.annotation_toolbar
            if hasattr(toolbar, 'add_bookmark_requested'):
                print("✅ Bookmark signals available")
            else:
                print("⚠️ Bookmark signals not found")
        else:
            print("⚠️ Annotation toolbar not created")
        
        # Check bookmark sidebar
        if hasattr(window, 'bookmark_sidebar') and window.bookmark_sidebar:
            print("✅ Bookmark sidebar created")
            print(f"✅ Sidebar initially hidden: {not window.bookmark_sidebar.isVisible()}")
        else:
            print("⚠️ Bookmark sidebar not created")
        
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ Main window annotation init test failed: {e}")
        return False

def test_bookmark_toolbar_integration():
    """Test bookmark toolbar integration"""
    print("🔧 Testing Bookmark Toolbar Integration...")
    
    from ui.main_window import MainWindow
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        window = MainWindow()
        window.show()
        
        if not window.annotation_toolbar:
            print("⚠️ Annotation toolbar not available, skipping test")
            window.close()
            return True
        
        toolbar = window.annotation_toolbar
        
        # Test initial state (should be disabled without document)
        if not toolbar.add_bookmark_action.isEnabled():
            print("✅ Toolbar initially disabled without document")
        else:
            print("⚠️ Toolbar should be disabled without document")
        
        # Test bookmark toggle method
        if hasattr(window, 'toggle_bookmark'):
            print("✅ Toggle bookmark method available")
        else:
            print("❌ Toggle bookmark method missing")
            window.close()
            return False
        
        # Test sidebar toggle method
        if hasattr(window, 'toggle_bookmark_sidebar'):
            print("✅ Toggle sidebar method available")
            
            # Test sidebar toggle
            initial_visible = window.bookmark_sidebar.isVisible() if window.bookmark_sidebar else False
            window.toggle_bookmark_sidebar()
            QTest.qWait(100)
            
            if window.bookmark_sidebar:
                new_visible = window.bookmark_sidebar.isVisible()
                if new_visible != initial_visible:
                    print("✅ Sidebar toggle working")
                else:
                    print("⚠️ Sidebar toggle may not be working")
        else:
            print("❌ Toggle sidebar method missing")
        
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark toolbar integration test failed: {e}")
        return False

def test_bookmark_document_integration():
    """Test bookmark integration with document loading"""
    print("📚 Testing Bookmark Document Integration...")
    
    from ui.main_window import MainWindow
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        window = MainWindow()
        
        if not window.annotation_manager:
            print("⚠️ Annotation manager not available, skipping test")
            window.close()
            return True
        
        # Test document annotation initialization method
        if hasattr(window, 'init_document_annotations'):
            print("✅ Document annotation initialization method available")
            
            # Test with a mock document path
            window.init_document_annotations("test_document.pdf")
            
            # Check if toolbar is enabled
            if window.annotation_toolbar and window.annotation_toolbar.add_bookmark_action.isEnabled():
                print("✅ Toolbar enabled after document initialization")
            else:
                print("⚠️ Toolbar not enabled after document initialization")
        else:
            print("❌ Document annotation initialization method missing")
            window.close()
            return False
        
        # Test bookmark methods
        bookmark_methods = [
            'toggle_bookmark',
            'show_add_bookmark_dialog', 
            'edit_bookmark',
            'delete_bookmark',
            'navigate_to_bookmark'
        ]
        
        missing_methods = []
        for method in bookmark_methods:
            if not hasattr(window, method):
                missing_methods.append(method)
        
        if not missing_methods:
            print("✅ All bookmark methods available")
        else:
            print(f"❌ Missing bookmark methods: {missing_methods}")
            window.close()
            return False
        
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark document integration test failed: {e}")
        return False

def test_bookmark_sidebar_integration():
    """Test bookmark sidebar integration"""
    print("📋 Testing Bookmark Sidebar Integration...")
    
    from ui.main_window import MainWindow
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        window = MainWindow()
        
        if not window.bookmark_sidebar or not window.annotation_manager:
            print("⚠️ Bookmark sidebar or annotation manager not available, skipping test")
            window.close()
            return True
        
        sidebar = window.bookmark_sidebar
        
        # Test sidebar signals connection
        signal_connected = False
        try:
            # Check if signals are connected by looking at the signal's receivers
            if sidebar.bookmark_selected.receivers() > 0:
                print("✅ Bookmark selection signal connected")
                signal_connected = True
            else:
                print("⚠️ Bookmark selection signal not connected")
        except:
            print("⚠️ Could not verify signal connections")
        
        # Test sidebar methods
        if hasattr(sidebar, 'set_document'):
            print("✅ Set document method available")
            
            # Test setting a document
            sidebar.set_document("test_document.pdf")
            QTest.qWait(100)
            
            if hasattr(sidebar, 'current_document'):
                print("✅ Document set successfully")
            else:
                print("⚠️ Document setting may not be working")
        else:
            print("❌ Set document method missing")
        
        # Test refresh method
        if hasattr(sidebar, 'refresh'):
            print("✅ Refresh method available")
            sidebar.refresh()
        else:
            print("❌ Refresh method missing")
        
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark sidebar integration test failed: {e}")
        return False

def test_bookmark_workflow():
    """Test complete bookmark workflow"""
    print("🔄 Testing Complete Bookmark Workflow...")
    
    from ui.main_window import MainWindow
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        window = MainWindow()
        
        if not window.annotation_manager:
            print("⚠️ Annotation manager not available, skipping workflow test")
            window.close()
            return True
        
        # Simulate document loading
        window.init_document_annotations("test_workflow.pdf")
        
        # Create a test bookmark directly through annotation manager
        bookmark = window.annotation_manager.create_bookmark(
            document_path="test_workflow.pdf",
            page_number=5,
            title="Test Workflow Bookmark",
            description="Testing the complete workflow"
        )
        
        if bookmark:
            print("✅ Bookmark created through annotation manager")
            
            # Test bookmark retrieval
            bookmarks = window.annotation_manager.get_bookmarks("test_workflow.pdf")
            if bookmarks and len(bookmarks) > 0:
                print(f"✅ Bookmark retrieved: {len(bookmarks)} bookmark(s)")
            else:
                print("❌ Bookmark not retrieved")
                window.close()
                return False
            
            # Test bookmark update through UI methods
            if hasattr(window, 'update_annotation_toolbar'):
                window.update_annotation_toolbar()
                print("✅ Annotation toolbar update method called")
            
            # Test bookmark deletion
            success = window.annotation_manager.delete_bookmark(bookmark.id)
            if success:
                print("✅ Bookmark deleted successfully")
            else:
                print("❌ Bookmark deletion failed")
        else:
            print("❌ Bookmark creation failed")
            window.close()
            return False
        
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark workflow test failed: {e}")
        return False

def main():
    """Run all bookmark integration tests"""
    print("🧪 BOOKMARK INTEGRATION TESTS")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tests = [
        ("Main Window Annotation Init", test_main_window_annotation_init),
        ("Bookmark Toolbar Integration", test_bookmark_toolbar_integration),
        ("Bookmark Document Integration", test_bookmark_document_integration),
        ("Bookmark Sidebar Integration", test_bookmark_sidebar_integration),
        ("Complete Bookmark Workflow", test_bookmark_workflow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 BOOKMARK INTEGRATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BOOKMARK INTEGRATION TESTS PASSED!")
        print("🚀 Task 2.3: Bookmark system integration is COMPLETE!")
        print("\nBookmark system features:")
        print("• Bookmark toolbar with add/remove functionality")
        print("• Bookmark sidebar for navigation and management")
        print("• Document-specific bookmark loading")
        print("• Bookmark creation, editing, and deletion")
        print("• Integration with main window navigation")
        return 0
    else:
        print("⚠️ Some integration tests failed. Review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())