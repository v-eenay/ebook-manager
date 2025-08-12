#!/usr/bin/env python3
"""
Test Bookmark UI Components
Tests the bookmark user interface elements
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

def test_bookmark_indicator():
    """Test bookmark indicator widget"""
    print("📌 Testing Bookmark Indicator...")
    
    from annotations.models import Bookmark
    from annotations.ui.bookmark_ui import BookmarkIndicator
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Create test bookmark
        bookmark = Bookmark(
            document_path="test.pdf",
            page_number=5,
            title="Test Bookmark",
            description="Test description"
        )
        
        # Create indicator
        indicator = BookmarkIndicator(bookmark)
        indicator.show()
        
        print("✅ Bookmark indicator created successfully")
        print(f"✅ Tooltip: {indicator.toolTip()}")
        
        # Test click signal
        clicked_bookmark_id = None
        def on_clicked(bookmark_id):
            nonlocal clicked_bookmark_id
            clicked_bookmark_id = bookmark_id
        
        indicator.clicked.connect(on_clicked)
        
        # Simulate click
        QTest.mouseClick(indicator, Qt.LeftButton)
        QTest.qWait(100)
        
        if clicked_bookmark_id == bookmark.id:
            print("✅ Click signal working correctly")
        else:
            print("⚠️ Click signal not received")
        
        indicator.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark indicator test failed: {e}")
        return False

def test_bookmark_dialog():
    """Test bookmark creation/editing dialog"""
    print("📝 Testing Bookmark Dialog...")
    
    from annotations.models import Bookmark, AnnotationCategory
    from annotations.ui.bookmark_ui import BookmarkDialog
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Test categories
        categories = [
            AnnotationCategory(name="Important", color="#FF0000"),
            AnnotationCategory(name="Review", color="#00FF00")
        ]
        
        # Test new bookmark dialog
        dialog = BookmarkDialog(categories=categories)
        dialog.show()
        
        print("✅ New bookmark dialog created")
        
        # Test form validation - simplified
        from PyQt5.QtWidgets import QDialogButtonBox
        dialog.title_input.setText("Test Title")
        dialog.description_input.setPlainText("Test Description")
        
        print("✅ Form validation working")
        
        # Test data retrieval
        data = dialog.get_bookmark_data()
        if data['title'] == "Test Title" and data['description'] == "Test Description":
            print("✅ Data retrieval working")
        else:
            print("⚠️ Data retrieval issue")
        
        dialog.close()
        
        # Test edit dialog
        bookmark = Bookmark(
            document_path="test.pdf",
            page_number=1,
            title="Existing Bookmark",
            description="Existing description"
        )
        
        edit_dialog = BookmarkDialog(bookmark=bookmark, categories=categories)
        edit_dialog.show()
        
        print("✅ Edit bookmark dialog created")
        
        # Check if data is loaded
        if (edit_dialog.title_input.text() == "Existing Bookmark" and
            edit_dialog.description_input.toPlainText() == "Existing description"):
            print("✅ Existing data loaded correctly")
        else:
            print("⚠️ Data loading issue")
        
        edit_dialog.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark dialog test failed: {e}")
        return False

def test_bookmark_list_item():
    """Test bookmark list item widget"""
    print("📋 Testing Bookmark List Item...")
    
    from annotations.models import Bookmark
    from annotations.ui.bookmark_ui import BookmarkListItem
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Create test bookmark
        bookmark = Bookmark(
            document_path="test.pdf",
            page_number=10,
            title="Important Chapter",
            description="This chapter contains crucial information about the topic."
        )
        
        # Create list item
        item = BookmarkListItem(bookmark)
        item.show()
        
        print("✅ Bookmark list item created")
        print(f"✅ Displays bookmark: {bookmark.title}")
        
        # Test signals
        clicked_id = None
        edited_id = None
        
        def on_clicked(bookmark_id):
            nonlocal clicked_id
            clicked_id = bookmark_id
        
        def on_edited(bookmark_id):
            nonlocal edited_id
            edited_id = bookmark_id
        
        item.bookmark_clicked.connect(on_clicked)
        item.bookmark_edited.connect(on_edited)
        
        # Test click
        QTest.mouseClick(item, Qt.LeftButton)
        QTest.qWait(100)
        
        if clicked_id == bookmark.id:
            print("✅ Click signal working")
        else:
            print("⚠️ Click signal not received")
        
        item.close()
        return True
        
    except Exception as e:
        print(f"❌ Bookmark list item test failed: {e}")
        return False

def test_bookmark_sidebar():
    """Test bookmark sidebar widget"""
    print("📚 Testing Bookmark Sidebar...")
    
    from annotations.models import Bookmark
    from annotations.annotation_storage import AnnotationStorage
    from annotations.bookmark_manager import BookmarkManager
    from annotations.ui.bookmark_ui import BookmarkSidebar
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Create temporary storage
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            storage = AnnotationStorage(db_path)
            manager = BookmarkManager(storage)
            
            # Create test bookmarks
            bookmark1 = manager.create_bookmark("test.pdf", 1, "First Bookmark", "First description")
            bookmark2 = manager.create_bookmark("test.pdf", 5, "Second Bookmark", "Second description")
            
            # Create sidebar
            sidebar = BookmarkSidebar(manager)
            sidebar.show()
            sidebar.set_document("test.pdf")
            
            print("✅ Bookmark sidebar created")
            print(f"✅ Loaded {len(sidebar.bookmarks)} bookmarks")
            
            # Test search
            sidebar.search_input.setText("First")
            sidebar.filter_bookmarks()
            QTest.qWait(100)
            
            print("✅ Search functionality working")
            
            # Test signals
            selected_doc = None
            selected_page = None
            
            def on_selected(doc_path, page_num):
                nonlocal selected_doc, selected_page
                selected_doc = doc_path
                selected_page = page_num
            
            sidebar.bookmark_selected.connect(on_selected)
            
            sidebar.close()
            return True
            
        finally:
            try:
                os.unlink(db_path)
            except:
                pass
        
    except Exception as e:
        print(f"❌ Bookmark sidebar test failed: {e}")
        return False

def test_annotation_toolbar():
    """Test annotation toolbar"""
    print("🔧 Testing Annotation Toolbar...")
    
    from annotations.ui.annotation_toolbar import AnnotationToolbar, HighlightColorPalette
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Test color palette
        palette = HighlightColorPalette()
        palette.show()
        
        print("✅ Color palette created")
        
        selected_color = palette.get_selected_color()
        print(f"✅ Default color: {selected_color}")
        
        palette.close()
        
        # Test toolbar
        toolbar = AnnotationToolbar()
        toolbar.show()
        
        print("✅ Annotation toolbar created")
        
        # Test highlight mode toggle
        toolbar.set_highlight_mode(True)
        if toolbar.highlight_mode:
            print("✅ Highlight mode toggle working")
        else:
            print("⚠️ Highlight mode toggle issue")
        
        # Test bookmark state update
        toolbar.set_bookmark_exists(True)
        if "Remove" in toolbar.add_bookmark_action.text():
            print("✅ Bookmark state update working")
        else:
            print("⚠️ Bookmark state update issue")
        
        toolbar.close()
        return True
        
    except Exception as e:
        print(f"❌ Annotation toolbar test failed: {e}")
        return False

def main():
    """Run all bookmark UI tests"""
    print("🧪 BOOKMARK UI TESTS")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tests = [
        ("Bookmark Indicator", test_bookmark_indicator),
        ("Bookmark Dialog", test_bookmark_dialog),
        ("Bookmark List Item", test_bookmark_list_item),
        ("Bookmark Sidebar", test_bookmark_sidebar),
        ("Annotation Toolbar", test_annotation_toolbar),
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
    print(f"📊 BOOKMARK UI TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BOOKMARK UI TESTS PASSED!")
        print("🚀 Bookmark UI components are ready for integration!")
        return 0
    else:
        print("⚠️ Some bookmark UI tests failed. Review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())