"""
MOBI Reader
Handles MOBI document reading.
Note: This is a basic implementation. For full MOBI support, consider using kindle-unpack or mobidedrm.
"""

import struct
from .base_reader import BaseReader


class MOBIReader(BaseReader):
    """Basic MOBI document reader."""
    
    def __init__(self):
        super().__init__()
        self.content = ""
        self.title = ""
        
    def load(self, file_path: str) -> bool:
        """Load a MOBI document."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Basic MOBI parsing - this is simplified
            # In a production app, you'd want to use a proper MOBI library
            
            # Check if it's a MOBI file
            if data[:4] != b'TPZ3' and data[60:68] != b'BOOKMOBI':
                raise ValueError("Not a valid MOBI file")
                
            self.file_path = file_path
            
            # Try to extract basic information
            # This is a very basic implementation
            try:
                # Look for text content (simplified)
                # In reality, MOBI files are complex and need proper parsing
                text_start = data.find(b'<html')
                if text_start == -1:
                    text_start = data.find(b'<HTML')
                    
                if text_start != -1:
                    # Find the end of HTML content
                    text_end = data.rfind(b'</html>')
                    if text_end == -1:
                        text_end = data.rfind(b'</HTML>')
                    if text_end == -1:
                        text_end = len(data)
                    else:
                        text_end += 7  # Include </html>
                        
                    html_content = data[text_start:text_end].decode('utf-8', errors='ignore')
                    
                    # Parse HTML to extract text
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                        
                    # Get text
                    self.content = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in self.content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    self.content = '\n'.join(chunk for chunk in chunks if chunk)
                    
                else:
                    # Fallback: try to extract any readable text
                    self.content = data.decode('utf-8', errors='ignore')
                    
            except Exception as e:
                # If HTML parsing fails, try to extract raw text
                self.content = data.decode('utf-8', errors='ignore')
                
            # Split content into pages (approximate)
            # Each "page" is roughly 2000 characters
            self.pages = []
            page_size = 2000
            
            if self.content:
                for i in range(0, len(self.content), page_size):
                    page_content = self.content[i:i + page_size]
                    # Try to break at sentence boundaries
                    if i + page_size < len(self.content):
                        last_period = page_content.rfind('.')
                        last_newline = page_content.rfind('\n')
                        break_point = max(last_period, last_newline)
                        if break_point > page_size * 0.8:  # Only break if it's not too early
                            page_content = page_content[:break_point + 1]
                    
                    self.pages.append(page_content.strip())
            else:
                self.pages = ["No readable content found in this MOBI file."]
                
            self.page_count = len(self.pages)
            self.is_loaded = True
            
            # Basic metadata
            self.metadata = {
                'title': 'MOBI Document',
                'author': 'Unknown',
                'format': 'MOBI'
            }
            
            return True
            
        except Exception as e:
            self.close()
            raise Exception(f"Failed to load MOBI: {str(e)}")
            
    def get_page(self, page_index: int) -> str:
        """Get a page as text."""
        if not self.is_loaded or not self.pages:
            raise RuntimeError("No document loaded")
            
        if page_index < 0 or page_index >= len(self.pages):
            raise IndexError(f"Page index {page_index} out of range (0-{len(self.pages)-1})")
            
        return self.pages[page_index]
        
    def get_page_count(self) -> int:
        """Get the total number of pages."""
        return len(self.pages) if self.is_loaded else 0
        
    def search_text(self, query: str) -> list:
        """Search for text in the document."""
        if not self.is_loaded:
            raise RuntimeError("No document loaded")
            
        results = []
        query_lower = query.lower()
        
        for i, page_content in enumerate(self.pages):
            if query_lower in page_content.lower():
                start_pos = page_content.lower().find(query_lower)
                if start_pos != -1:
                    # Get some context around the match
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(page_content), start_pos + len(query) + 50)
                    context = page_content[context_start:context_end]
                    
                    results.append({
                        'page': i,
                        'context': context,
                        'position': start_pos
                    })
                    
        return results
        
    def close(self):
        """Close the MOBI document."""
        self.content = ""
        self.pages = []
        super().close()
