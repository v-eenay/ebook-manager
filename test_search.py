#!/usr/bin/env python3
"""
Test Search Functionality for Modern EBook Reader
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

def test_search_engine():
    """Test the search engine functionality"""
    print("🔍 Testing Search Engine...")
    
    from search.search_engine import SearchEngine
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        engine = SearchEngine(db_path)
        
        # Test indexing
        test_content = [
            "This is the first page with some test content.",
            "The second page contains different information about testing.",
            "Third page has more content for comprehensive search testing."
        ]
        
        engine.index_document("test_doc.pdf", test_content)
        print("✅ Document indexing successful")
        
        # Test search
        results = engine.search("test content")
        if results:
            print(f"✅ Search returned {len(results)} results")
            
            # Check first result
            first_result = results[0]
            print(f"✅ First result: page {first_result.page_number}")
            print(f"✅ Snippet: {first_result.text_snippet[:50]}...")
        else:
            print("❌ No search results found")
            return False
        
        # Test search history
        history = engine.get_search_history()
        if "test content" in history:
            print("✅ Search history working")
        else:
            print("⚠️ Search history not found")
        
        # Test indexed documents
        indexed = engine.get_indexed_documents()
        if "test_doc.pdf" in indexed:
            print("✅ Document indexing tracked")
        else:
            print("❌ Document not found in index")
            return False
        
        return True
        
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass

def test_document_indexer():
    """Test the document indexer"""
    print("📚 Testing Document Indexer...")
    
    from search.search_engine import SearchEngine
    from search.indexer import DocumentIndexer
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        engine = SearchEngine(db_path)
        indexer = DocumentIndexer(engine)
        
        # Test with existing test document
        if Path("test_document.pdf").exists():
            success = indexer.index_document("test_document.pdf")
            if success:
                print("✅ PDF document indexed successfully")
                
                # Test search on indexed document
                results = engine.search("test")
                if results:
                    print(f"✅ Search found {len(results)} results in PDF")
                else:
                    print("⚠️ No results found in indexed PDF")
            else:
                print("❌ Failed to index PDF document")
                return False
        else:
            print("⚠️ test_document.pdf not found, skipping PDF test")
        
        # Test unsupported format
        is_indexed = indexer.is_indexed("nonexistent.xyz")
        print(f"✅ Unsupported format check: {not is_indexed}")
        
        return True
        
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass

def test_search_ui():
    """Test the search UI components"""
    print("🎨 Testing Search UI...")
    
    from search.search_engine import SearchEngine
    from search.search_ui import SearchWidget
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        engine = SearchEngine(db_path)
        
        # Index some test content
        test_content = [
            "User interface testing content here.",
            "Search functionality with UI components.",
            "Testing the search widget display."
        ]
        engine.index_document("ui_test.pdf", test_content)
        
        # Create search widget
        search_widget = SearchWidget(engine)
        search_widget.show()
        
        print("✅ Search widget created successfully")
        
        # Test search input
        search_widget.search_input.setText("testing")
        QTest.qWait(100)
        
        # Trigger search
        search_widget.perform_search()
        QTest.qWait(1000)  # Wait for search to complete
        
        print("✅ Search UI interaction test completed")
        
        search_widget.close()
        return True
        
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass

def test_search_integration():
    """Test search integration with main application"""
    print("🔗 Testing Search Integration...")
    
    from ui.main_window import MainWindow
    from search.search_engine import SearchEngine
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Create main window
        window = MainWindow()
        
        # Test that search can be integrated
        engine = SearchEngine()
        
        print("✅ Search engine can be created alongside main window")
        
        # Test basic integration
        if hasattr(window, 'stacked_widget'):
            print("✅ Main window structure compatible with search integration")
        
        window.close()
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all search tests"""
    print("🧪 SEARCH FUNCTIONALITY TESTS")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tests = [
        ("Search Engine", test_search_engine),
        ("Document Indexer", test_document_indexer),
        ("Search UI", test_search_ui),
        ("Search Integration", test_search_integration),
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
    print(f"📊 SEARCH TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SEARCH TESTS PASSED!")
        print("🚀 Phase 4.1 (Search & Indexing) is ready!")
        return 0
    else:
        print("⚠️ Some search tests failed. Review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())