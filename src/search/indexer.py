"""
Document Indexer for Modern EBook Reader
Handles document content extraction and indexing
"""

import logging
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger("ebook_reader")

class DocumentIndexer:
    """Handles document indexing for search functionality"""
    
    def __init__(self, search_engine):
        """Initialize indexer with search engine"""
        self.search_engine = search_engine
        self.supported_formats = {'.pdf', '.epub', '.mobi', '.txt'}
    
    def index_document(self, document_path: str) -> bool:
        """Index a single document"""
        try:
            path = Path(document_path)
            
            if not path.exists():
                logger.error(f"Document not found: {document_path}")
                return False
            
            if path.suffix.lower() not in self.supported_formats:
                logger.warning(f"Unsupported format: {path.suffix}")
                return False
            
            # Extract text content from document
            content = self._extract_content(document_path)
            
            if not content:
                logger.warning(f"No content extracted from: {document_path}")
                return False
            
            # Index the content
            self.search_engine.index_document(document_path, content)
            logger.info(f"Successfully indexed: {document_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {document_path}: {e}")
            return False
    
    def index_documents(self, document_paths: List[str], max_workers: int = 4) -> int:
        """Index multiple documents concurrently"""
        indexed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all indexing tasks
            future_to_path = {
                executor.submit(self.index_document, path): path 
                for path in document_paths
            }
            
            # Process completed tasks
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    if future.result():
                        indexed_count += 1
                except Exception as e:
                    logger.error(f"Indexing failed for {path}: {e}")
        
        logger.info(f"Indexed {indexed_count}/{len(document_paths)} documents")
        return indexed_count
    
    def _extract_content(self, document_path: str) -> Optional[List[str]]:
        """Extract text content from document"""
        path = Path(document_path)
        extension = path.suffix.lower()
        
        try:
            if extension == '.pdf':
                return self._extract_pdf_content(document_path)
            elif extension == '.epub':
                return self._extract_epub_content(document_path)
            elif extension == '.mobi':
                return self._extract_mobi_content(document_path)
            elif extension == '.txt':
                return self._extract_txt_content(document_path)
            else:
                logger.warning(f"Unsupported format: {extension}")
                return None
                
        except Exception as e:
            logger.error(f"Content extraction failed for {document_path}: {e}")
            return None
    
    def _extract_pdf_content(self, document_path: str) -> List[str]:
        """Extract content from PDF using existing PDF reader"""
        try:
            from readers.pdf_reader import PDFReader
            
            reader = PDFReader()
            if reader.load(document_path):
                content = []
                for page_num in range(reader.get_page_count()):
                    page_text = reader.get_page_text(page_num)
                    content.append(page_text or "")
                return content
            else:
                logger.error(f"Failed to load PDF: {document_path}")
                return []
                
        except Exception as e:
            logger.error(f"PDF content extraction failed: {e}")
            return []
    
    def _extract_epub_content(self, document_path: str) -> List[str]:
        """Extract content from EPUB"""
        try:
            from readers.epub_reader import EPUBReader
            
            reader = EPUBReader()
            if reader.load(document_path):
                content = []
                for page_num in range(reader.get_page_count()):
                    page_text = reader.get_page_text(page_num)
                    content.append(page_text or "")
                return content
            else:
                logger.error(f"Failed to load EPUB: {document_path}")
                return []
                
        except Exception as e:
            logger.error(f"EPUB content extraction failed: {e}")
            return []
    
    def _extract_mobi_content(self, document_path: str) -> List[str]:
        """Extract content from MOBI"""
        try:
            from readers.mobi_reader import MOBIReader
            
            reader = MOBIReader()
            if reader.load(document_path):
                content = []
                for page_num in range(reader.get_page_count()):
                    page_text = reader.get_page_text(page_num)
                    content.append(page_text or "")
                return content
            else:
                logger.error(f"Failed to load MOBI: {document_path}")
                return []
                
        except Exception as e:
            logger.error(f"MOBI content extraction failed: {e}")
            return []
    
    def _extract_txt_content(self, document_path: str) -> List[str]:
        """Extract content from plain text file"""
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into pages (approximate)
            lines_per_page = 50
            lines = content.split('\n')
            pages = []
            
            for i in range(0, len(lines), lines_per_page):
                page_lines = lines[i:i + lines_per_page]
                pages.append('\n'.join(page_lines))
            
            return pages if pages else [content]
            
        except Exception as e:
            logger.error(f"Text file extraction failed: {e}")
            return []
    
    def reindex_all(self) -> int:
        """Reindex all previously indexed documents"""
        try:
            indexed_docs = self.search_engine.get_indexed_documents()
            
            if not indexed_docs:
                logger.info("No documents to reindex")
                return 0
            
            # Clear existing index
            self.search_engine.clear_index()
            
            # Reindex all documents
            return self.index_documents(indexed_docs)
            
        except Exception as e:
            logger.error(f"Reindexing failed: {e}")
            return 0
    
    def is_indexed(self, document_path: str) -> bool:
        """Check if document is already indexed"""
        indexed_docs = self.search_engine.get_indexed_documents()
        return document_path in indexed_docs