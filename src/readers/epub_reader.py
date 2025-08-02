"""
EPUB Reader
Handles EPUB document reading using ebooklib.
"""

try:
    import ebooklib
    from ebooklib import epub
    EBOOKLIB_AVAILABLE = True
except ImportError:
    EBOOKLIB_AVAILABLE = False

import html
from bs4 import BeautifulSoup
from .base_reader import BaseReader


class EPUBReader(BaseReader):
    """EPUB document reader using ebooklib."""
    
    def __init__(self):
        super().__init__()
        self.book = None
        self.chapters = []
        
        if not EBOOKLIB_AVAILABLE:
            raise ImportError("ebooklib is required for EPUB support. Install with: pip install ebooklib")
            
    def load(self, file_path: str) -> bool:
        """Load an EPUB document."""
        try:
            self.book = epub.read_epub(file_path)
            self.file_path = file_path
            
            # Extract chapters
            self.chapters = []
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    self.chapters.append(item)
                    
            self.page_count = len(self.chapters)
            self.is_loaded = True
            
            # Extract metadata
            self.metadata = {
                'title': self.book.get_metadata('DC', 'title')[0][0] if self.book.get_metadata('DC', 'title') else '',
                'author': self.book.get_metadata('DC', 'creator')[0][0] if self.book.get_metadata('DC', 'creator') else '',
                'language': self.book.get_metadata('DC', 'language')[0][0] if self.book.get_metadata('DC', 'language') else '',
                'publisher': self.book.get_metadata('DC', 'publisher')[0][0] if self.book.get_metadata('DC', 'publisher') else '',
                'description': self.book.get_metadata('DC', 'description')[0][0] if self.book.get_metadata('DC', 'description') else '',
            }
            
            return True
            
        except Exception as e:
            self.close()
            raise Exception(f"Failed to load EPUB: {str(e)}")
            
    def get_page(self, page_index: int) -> str:
        """Get a chapter/page as HTML text."""
        if not self.is_loaded or not self.chapters:
            raise RuntimeError("No document loaded")
            
        if page_index < 0 or page_index >= len(self.chapters):
            raise IndexError(f"Page index {page_index} out of range (0-{len(self.chapters)-1})")
            
        try:
            chapter = self.chapters[page_index]
            content = chapter.get_content().decode('utf-8')
            
            # Parse HTML and extract text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text if text else "No content available for this chapter."
            
        except Exception as e:
            raise Exception(f"Failed to read chapter {page_index}: {str(e)}")
            
    def get_page_count(self) -> int:
        """Get the total number of chapters."""
        return len(self.chapters) if self.is_loaded else 0
        
    def get_chapter_title(self, page_index: int) -> str:
        """Get the title of a specific chapter."""
        if not self.is_loaded or page_index < 0 or page_index >= len(self.chapters):
            return ""
            
        try:
            chapter = self.chapters[page_index]
            content = chapter.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Try to find a title in various ways
            title_tag = soup.find(['h1', 'h2', 'h3', 'title'])
            if title_tag:
                return title_tag.get_text().strip()
                
            # Fallback to filename
            return chapter.get_name()
            
        except Exception:
            return f"Chapter {page_index + 1}"
            
    def get_table_of_contents(self) -> list:
        """Get the table of contents."""
        if not self.is_loaded:
            return []
            
        toc = []
        for i, chapter in enumerate(self.chapters):
            title = self.get_chapter_title(i)
            toc.append({
                'index': i,
                'title': title,
                'filename': chapter.get_name()
            })
            
        return toc
        
    def search_text(self, query: str) -> list:
        """Search for text in the document."""
        if not self.is_loaded:
            raise RuntimeError("No document loaded")
            
        results = []
        query_lower = query.lower()
        
        for i, chapter in enumerate(self.chapters):
            try:
                content = self.get_page(i)
                if query_lower in content.lower():
                    # Find the position and context
                    start_pos = content.lower().find(query_lower)
                    if start_pos != -1:
                        # Get some context around the match
                        context_start = max(0, start_pos - 50)
                        context_end = min(len(content), start_pos + len(query) + 50)
                        context = content[context_start:context_end]
                        
                        results.append({
                            'chapter': i,
                            'chapter_title': self.get_chapter_title(i),
                            'context': context,
                            'position': start_pos
                        })
            except Exception:
                continue
                
        return results
        
    def close(self):
        """Close the EPUB document."""
        self.book = None
        self.chapters = []
        super().close()
