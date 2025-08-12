#!/usr/bin/env python3
"""
Unit Tests for Annotation System
Tests all annotation functionality including models, storage, and managers
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from annotations.models import (
    Annotation, Bookmark, Highlight, Note, AnnotationCategory,
    Point, TextSelection, AnnotationType, HighlightColor
)
from annotations.annotation_storage import AnnotationStorage
from annotations.annotation_manager import AnnotationManager
from annotations.bookmark_manager import BookmarkManager
from annotations.highlight_manager import HighlightManager
from annotations.note_manager import NoteManager

class TestAnnotationModels(unittest.TestCase):
    """Test annotation data models"""
    
    def test_point_creation(self):
        """Test Point model creation and serialization"""
        point = Point(10.5, 20.3)
        self.assertEqual(point.x, 10.5)
        self.assertEqual(point.y, 20.3)
        
        # Test serialization
        data = point.to_dict()
        self.assertEqual(data, {"x": 10.5, "y": 20.3})
        
        # Test deserialization
        point2 = Point.from_dict(data)
        self.assertEqual(point2.x, point.x)
        self.assertEqual(point2.y, point.y)
    
    def test_text_selection_creation(self):
        """Test TextSelection model creation and serialization"""
        start_pos = Point(0, 0)
        end_pos = Point(100, 20)
        selection = TextSelection(start_pos, end_pos, 0, 50, "selected text")
        
        self.assertEqual(selection.start_char_index, 0)
        self.assertEqual(selection.end_char_index, 50)
        self.assertEqual(selection.selected_text, "selected text")
        
        # Test serialization
        data = selection.to_dict()
        self.assertIn("start_position", data)
        self.assertIn("end_position", data)
        self.assertEqual(data["selected_text"], "selected text")
        
        # Test deserialization
        selection2 = TextSelection.from_dict(data)
        self.assertEqual(selection2.selected_text, selection.selected_text)
    
    def test_bookmark_creation(self):
        """Test Bookmark model creation and serialization"""
        bookmark = Bookmark(
            document_path="test.pdf",
            page_number=5,
            title="Important Page",
            description="This page contains important information"
        )
        
        self.assertEqual(bookmark.get_type(), AnnotationType.BOOKMARK)
        self.assertEqual(bookmark.page_number, 5)
        self.assertEqual(bookmark.title, "Important Page")
        self.assertEqual(bookmark.get_display_text(), "Important Page")
        
        # Test serialization
        data = bookmark.to_dict()
        self.assertEqual(data["title"], "Important Page")
        self.assertEqual(data["page_number"], 5)
        
        # Test deserialization
        bookmark2 = Bookmark.from_dict(data)
        self.assertEqual(bookmark2.title, bookmark.title)
        self.assertEqual(bookmark2.page_number, bookmark.page_number)
    
    def test_highlight_creation(self):
        """Test Highlight model creation and serialization"""
        selection = TextSelection(Point(0, 0), Point(100, 20), 0, 50, "highlighted text")
        highlight = Highlight(
            document_path="test.pdf",
            page_number=3,
            text_selection=selection,
            highlighted_text="highlighted text",
            color=HighlightColor.YELLOW.value
        )
        
        self.assertEqual(highlight.get_type(), AnnotationType.HIGHLIGHT)
        self.assertEqual(highlight.color, HighlightColor.YELLOW.value)
        self.assertEqual(highlight.highlighted_text, "highlighted text")
        
        # Test serialization
        data = highlight.to_dict()
        self.assertEqual(data["color"], HighlightColor.YELLOW.value)
        self.assertIn("text_selection", data)
        
        # Test deserialization
        highlight2 = Highlight.from_dict(data)
        self.assertEqual(highlight2.color, highlight.color)
        self.assertEqual(highlight2.highlighted_text, highlight.highlighted_text)
    
    def test_note_creation(self):
        """Test Note model creation and serialization"""
        position = Point(50, 100)
        note = Note(
            document_path="test.pdf",
            page_number=2,
            position=position,
            content="<p>This is a note</p>",
            plain_text="This is a note"
        )
        
        self.assertEqual(note.get_type(), AnnotationType.NOTE)
        self.assertEqual(note.plain_text, "This is a note")
        self.assertEqual(note.position.x, 50)
        
        # Test serialization
        data = note.to_dict()
        self.assertEqual(data["plain_text"], "This is a note")
        self.assertIn("position", data)
        
        # Test deserialization
        note2 = Note.from_dict(data)
        self.assertEqual(note2.plain_text, note.plain_text)
        self.assertEqual(note2.position.x, note.position.x)

class TestAnnotationStorage(unittest.TestCase):
    """Test annotation storage functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.storage = AnnotationStorage(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Database should be created and initialized
        self.assertTrue(Path(self.temp_db.name).exists())
        
        # Should have default categories
        categories = self.storage.get_categories()
        self.assertGreater(len(categories), 0)
    
    def test_bookmark_storage(self):
        """Test bookmark save and load operations"""
        bookmark = Bookmark(
            document_path="test.pdf",
            page_number=1,
            title="Test Bookmark",
            description="Test description"
        )
        
        # Save bookmark
        success = self.storage.save_annotation(bookmark)
        self.assertTrue(success)
        
        # Load bookmark
        loaded_bookmark = self.storage.load_annotation(bookmark.id)
        self.assertIsNotNone(loaded_bookmark)
        self.assertIsInstance(loaded_bookmark, Bookmark)
        self.assertEqual(loaded_bookmark.title, "Test Bookmark")
    
    def test_highlight_storage(self):
        """Test highlight save and load operations"""
        selection = TextSelection(Point(0, 0), Point(100, 20), 0, 50, "test text")
        highlight = Highlight(
            document_path="test.pdf",
            page_number=1,
            text_selection=selection,
            highlighted_text="test text",
            color=HighlightColor.YELLOW.value
        )
        
        # Save highlight
        success = self.storage.save_annotation(highlight)
        self.assertTrue(success)
        
        # Load highlight
        loaded_highlight = self.storage.load_annotation(highlight.id)
        self.assertIsNotNone(loaded_highlight)
        self.assertIsInstance(loaded_highlight, Highlight)
        self.assertEqual(loaded_highlight.highlighted_text, "test text")
    
    def test_note_storage(self):
        """Test note save and load operations"""
        note = Note(
            document_path="test.pdf",
            page_number=1,
            position=Point(50, 100),
            content="Test note content",
            plain_text="Test note content"
        )
        
        # Save note
        success = self.storage.save_annotation(note)
        self.assertTrue(success)
        
        # Load note
        loaded_note = self.storage.load_annotation(note.id)
        self.assertIsNotNone(loaded_note)
        self.assertIsInstance(loaded_note, Note)
        self.assertEqual(loaded_note.plain_text, "Test note content")
    
    def test_annotation_search(self):
        """Test annotation search functionality"""
        # Create test annotations
        bookmark = Bookmark(
            document_path="test.pdf",
            page_number=1,
            title="Searchable Bookmark",
            description="Contains search terms"
        )
        
        note = Note(
            document_path="test.pdf",
            page_number=2,
            position=Point(0, 0),
            content="Searchable note content",
            plain_text="Searchable note content"
        )
        
        # Save annotations
        self.storage.save_annotation(bookmark)
        self.storage.save_annotation(note)
        
        # Search for annotations
        results = self.storage.search_annotations("Searchable")
        self.assertGreater(len(results), 0)
        
        # Check that results contain our annotations
        result_ids = [r.annotation.id for r in results]
        self.assertIn(bookmark.id, result_ids)
        self.assertIn(note.id, result_ids)
    
    def test_category_management(self):
        """Test category save and load operations"""
        category = AnnotationCategory(
            name="Test Category",
            color="#FF0000",
            description="Test category description"
        )
        
        # Save category
        success = self.storage.save_category(category)
        self.assertTrue(success)
        
        # Load categories
        categories = self.storage.get_categories()
        category_names = [c.name for c in categories]
        self.assertIn("Test Category", category_names)

class TestAnnotationManagers(unittest.TestCase):
    """Test annotation manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.manager = AnnotationManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_bookmark_manager(self):
        """Test bookmark manager operations"""
        # Create bookmark
        bookmark = self.manager.create_bookmark(
            "test.pdf", 1, "Test Bookmark", "Test description"
        )
        self.assertIsNotNone(bookmark)
        self.assertEqual(bookmark.title, "Test Bookmark")
        
        # Get bookmarks
        bookmarks = self.manager.get_bookmarks("test.pdf")
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0].title, "Test Bookmark")
        
        # Update bookmark
        bookmark.title = "Updated Bookmark"
        success = self.manager.update_bookmark(bookmark)
        self.assertTrue(success)
        
        # Verify update
        updated_bookmarks = self.manager.get_bookmarks("test.pdf")
        self.assertEqual(updated_bookmarks[0].title, "Updated Bookmark")
        
        # Delete bookmark
        success = self.manager.delete_bookmark(bookmark.id)
        self.assertTrue(success)
        
        # Verify deletion
        final_bookmarks = self.manager.get_bookmarks("test.pdf")
        self.assertEqual(len(final_bookmarks), 0)
    
    def test_highlight_manager(self):
        """Test highlight manager operations"""
        # Create highlight
        selection = TextSelection(Point(0, 0), Point(100, 20), 0, 50, "test text")
        highlight = self.manager.create_highlight(
            "test.pdf", 1, selection, HighlightColor.YELLOW.value
        )
        self.assertIsNotNone(highlight)
        self.assertEqual(highlight.color, HighlightColor.YELLOW.value)
        
        # Get highlights
        highlights = self.manager.get_highlights("test.pdf")
        self.assertEqual(len(highlights), 1)
        
        # Change color
        success = self.manager.change_highlight_color(highlight.id, HighlightColor.GREEN.value)
        self.assertTrue(success)
        
        # Verify color change
        updated_highlights = self.manager.get_highlights("test.pdf")
        self.assertEqual(updated_highlights[0].color, HighlightColor.GREEN.value)
    
    def test_note_manager(self):
        """Test note manager operations"""
        # Create note
        note = self.manager.create_note(
            "test.pdf", 1, Point(50, 100), "Test note content", "Test note content"
        )
        self.assertIsNotNone(note)
        self.assertEqual(note.plain_text, "Test note content")
        
        # Get notes
        notes = self.manager.get_notes("test.pdf")
        self.assertEqual(len(notes), 1)
        
        # Create reply
        reply = self.manager.note_manager.create_reply(
            note.id, "Reply content", "Reply content"
        )
        self.assertIsNotNone(reply)
        self.assertEqual(reply.parent_note_id, note.id)
        
        # Get note thread
        thread = self.manager.note_manager.get_note_thread(note.id)
        self.assertEqual(len(thread), 2)  # Original note + reply
    
    def test_annotation_search(self):
        """Test annotation search through manager"""
        # Create various annotations
        self.manager.create_bookmark("test.pdf", 1, "Searchable Bookmark")
        
        selection = TextSelection(Point(0, 0), Point(100, 20), 0, 50, "searchable text")
        self.manager.create_highlight("test.pdf", 2, selection, HighlightColor.YELLOW.value)
        
        self.manager.create_note("test.pdf", 3, Point(0, 0), "Searchable note", "Searchable note")
        
        # Search annotations
        results = self.manager.search_annotations("Searchable")
        self.assertGreaterEqual(len(results), 3)
    
    def test_category_management(self):
        """Test category management through manager"""
        # Create category
        category = self.manager.create_category("Test Category", "#FF0000", "Test description")
        self.assertIsNotNone(category)
        
        # Get categories
        categories = self.manager.get_categories()
        category_names = [c.name for c in categories]
        self.assertIn("Test Category", category_names)
        
        # Create annotation with category
        bookmark = self.manager.create_bookmark(
            "test.pdf", 1, "Categorized Bookmark", category=category.id
        )
        self.assertEqual(bookmark.category, category.id)

def run_annotation_tests():
    """Run all annotation tests"""
    print("🧪 ANNOTATION SYSTEM TESTS")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAnnotationModels))
    suite.addTests(loader.loadTestsFromTestCase(TestAnnotationStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestAnnotationManagers))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 ALL ANNOTATION TESTS PASSED!")
        print(f"✅ Ran {result.testsRun} tests successfully")
        return True
    else:
        print("❌ SOME ANNOTATION TESTS FAILED!")
        print(f"❌ Failures: {len(result.failures)}")
        print(f"❌ Errors: {len(result.errors)}")
        return False

if __name__ == "__main__":
    success = run_annotation_tests()
    sys.exit(0 if success else 1)