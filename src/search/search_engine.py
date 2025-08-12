"""
Search Engine for Modern EBook Reader
Provides full-text search capabilities with highlighting and filtering
"""

import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("ebook_reader")

@dataclass
class SearchResult:
    """Represents a search result with context"""
    document_path: str
    page_number: int
    text_snippet: str
    match_start: int
    match_end: int
    relevance_score: float = 0.0

class SearchEngine:
    """Advanced search engine with indexing and full-text search"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize search engine with database"""
        if db_path is None:
            db_path = str(Path.home() / '.ebook_reader' / 'search_index.db')
        
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the search database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS document_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_path TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(document_path, page_number)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create full-text search index
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
                    document_path,
                    page_number,
                    content,
                    content='document_index',
                    content_rowid='id'
                )
            ''')
            
            conn.commit()
    
    def index_document(self, document_path: str, pages_content: List[str]):
        """Index a document's content for searching"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Remove existing entries for this document
                conn.execute('DELETE FROM document_index WHERE document_path = ?', (document_path,))
                
                # Insert new content
                for page_num, content in enumerate(pages_content, 1):
                    if content.strip():  # Only index non-empty pages
                        conn.execute('''
                            INSERT OR REPLACE INTO document_index 
                            (document_path, page_number, content) 
                            VALUES (?, ?, ?)
                        ''', (document_path, page_num, content))
                
                # Update FTS index
                conn.execute('INSERT INTO content_fts(content_fts) VALUES("rebuild")')
                conn.commit()
                
                logger.info(f"Indexed document: {document_path} ({len(pages_content)} pages)")
                
        except Exception as e:
            logger.error(f"Failed to index document {document_path}: {e}")
    
    def search(self, query: str, max_results: int = 50) -> List[SearchResult]:
        """Perform full-text search across indexed documents"""
        if not query.strip():
            return []
        
        # Save search to history
        self.add_to_history(query)
        
        results = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Use FTS for efficient searching
                cursor = conn.execute('''
                    SELECT document_path, page_number, content, 
                           bm25(content_fts) as relevance
                    FROM content_fts 
                    WHERE content_fts MATCH ? 
                    ORDER BY relevance 
                    LIMIT ?
                ''', (query, max_results))
                
                for row in cursor.fetchall():
                    document_path, page_number, content, relevance = row
                    
                    # Find the best snippet with the search term
                    snippet, match_start, match_end = self._extract_snippet(content, query)
                    
                    result = SearchResult(
                        document_path=document_path,
                        page_number=page_number,
                        text_snippet=snippet,
                        match_start=match_start,
                        match_end=match_end,
                        relevance_score=abs(relevance)  # BM25 returns negative scores
                    )
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Fallback to simple text search
            results = self._simple_search(query, max_results)
        
        return results
    
    def _simple_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Fallback simple text search when FTS fails"""
        results = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT document_path, page_number, content 
                    FROM document_index 
                    WHERE content LIKE ? 
                    LIMIT ?
                ''', (f'%{query}%', max_results))
                
                for row in cursor.fetchall():
                    document_path, page_number, content = row
                    
                    snippet, match_start, match_end = self._extract_snippet(content, query)
                    
                    result = SearchResult(
                        document_path=document_path,
                        page_number=page_number,
                        text_snippet=snippet,
                        match_start=match_start,
                        match_end=match_end,
                        relevance_score=1.0
                    )
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"Simple search failed: {e}")
        
        return results
    
    def _extract_snippet(self, content: str, query: str, snippet_length: int = 200) -> Tuple[str, int, int]:
        """Extract a snippet around the search term"""
        # Find the first occurrence of the query (case-insensitive)
        match = re.search(re.escape(query), content, re.IGNORECASE)
        
        if not match:
            # If exact match not found, return beginning of content
            snippet = content[:snippet_length] + "..." if len(content) > snippet_length else content
            return snippet, 0, 0
        
        match_start = match.start()
        match_end = match.end()
        
        # Calculate snippet boundaries
        snippet_start = max(0, match_start - snippet_length // 2)
        snippet_end = min(len(content), match_start + snippet_length // 2)
        
        # Adjust to word boundaries
        if snippet_start > 0:
            word_start = content.rfind(' ', 0, snippet_start)
            if word_start != -1:
                snippet_start = word_start + 1
        
        if snippet_end < len(content):
            word_end = content.find(' ', snippet_end)
            if word_end != -1:
                snippet_end = word_end
        
        snippet = content[snippet_start:snippet_end]
        
        # Add ellipsis if needed
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(content):
            snippet = snippet + "..."
        
        # Adjust match positions relative to snippet
        relative_start = match_start - snippet_start
        relative_end = match_end - snippet_start
        
        if snippet_start > 0:  # Account for "..." prefix
            relative_start += 3
            relative_end += 3
        
        return snippet, relative_start, relative_end
    
    def add_to_history(self, query: str):
        """Add search query to history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('INSERT INTO search_history (query) VALUES (?)', (query,))
                
                # Keep only last 100 searches
                conn.execute('''
                    DELETE FROM search_history 
                    WHERE id NOT IN (
                        SELECT id FROM search_history 
                        ORDER BY searched_at DESC 
                        LIMIT 100
                    )
                ''')
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save search history: {e}")
    
    def get_search_history(self, limit: int = 20) -> List[str]:
        """Get recent search queries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT DISTINCT query 
                    FROM search_history 
                    ORDER BY searched_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get search history: {e}")
            return []
    
    def clear_index(self):
        """Clear all indexed content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM document_index')
                conn.execute('DELETE FROM content_fts')
                conn.commit()
                logger.info("Search index cleared")
                
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
    
    def get_indexed_documents(self) -> List[str]:
        """Get list of indexed documents"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT DISTINCT document_path FROM document_index')
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get indexed documents: {e}")
            return []