package reader

import (
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"
)

// MOBIDocument represents a MOBI document
type MOBIDocument struct {
	filename    string
	currentPage int
	pages       []string // Each page is a section of text
	title       string
	author      string
}

// NewMOBIDocument creates a new MOBI document
func NewMOBIDocument(filename string) (*MOBIDocument, error) {
	// For now, we'll implement a basic MOBI reader
	// This is a simplified implementation - a full MOBI parser would be more complex
	
	mobiDoc := &MOBIDocument{
		filename:    filename,
		currentPage: 1,
		title:       "MOBI Document",
		author:      "",
	}

	// Try to read basic content from MOBI file
	err := mobiDoc.extractBasicContent()
	if err != nil {
		return nil, fmt.Errorf("failed to extract MOBI content: %v", err)
	}

	return mobiDoc, nil
}

// extractBasicContent extracts basic content from MOBI file
// This is a simplified approach - real MOBI parsing requires understanding the format
func (m *MOBIDocument) extractBasicContent() error {
	// Read the file
	file, err := os.Open(m.filename)
	if err != nil {
		return err
	}
	defer file.Close()

	// Read file content
	content, err := io.ReadAll(file)
	if err != nil {
		return err
	}

	// Convert to string and try to extract text
	text := string(content)
	
	// Simple heuristic: look for readable text patterns
	// This is very basic and would need improvement for real MOBI files
	cleanText := m.extractReadableText(text)
	
	if cleanText == "" {
		// If no readable text found, create a placeholder
		cleanText = "MOBI content extraction not fully implemented.\n\nThis is a placeholder for MOBI file content. A complete MOBI parser would be needed to properly extract and display the book content."
	}

	// Split into pages
	m.splitIntoPages(cleanText)

	if len(m.pages) == 0 {
		return fmt.Errorf("no readable content found in MOBI")
	}

	return nil
}

// extractReadableText attempts to extract readable text from MOBI content
func (m *MOBIDocument) extractReadableText(content string) string {
	// Remove non-printable characters
	re := regexp.MustCompile(`[^\x20-\x7E\n\r\t]`)
	text := re.ReplaceAllString(content, " ")

	// Look for sequences of readable text
	lines := strings.Split(text, "\n")
	var readableLines []string

	for _, line := range lines {
		line = strings.TrimSpace(line)
		// Keep lines that look like readable text
		if len(line) > 10 && strings.Contains(line, " ") {
			// Remove excessive whitespace
			re := regexp.MustCompile(`\s+`)
			line = re.ReplaceAllString(line, " ")
			readableLines = append(readableLines, line)
		}
	}

	return strings.Join(readableLines, "\n\n")
}

// splitIntoPages splits content into manageable pages
func (m *MOBIDocument) splitIntoPages(text string) {
	// Split into pages of approximately 2000 characters each
	const pageSize = 2000
	words := strings.Fields(text)
	
	m.pages = make([]string, 0)
	currentPage := ""
	
	for _, word := range words {
		if len(currentPage)+len(word)+1 > pageSize && currentPage != "" {
			m.pages = append(m.pages, strings.TrimSpace(currentPage))
			currentPage = word
		} else {
			if currentPage != "" {
				currentPage += " "
			}
			currentPage += word
		}
	}
	
	// Add the last page if it has content
	if strings.TrimSpace(currentPage) != "" {
		m.pages = append(m.pages, strings.TrimSpace(currentPage))
	}
}

// GetTitle returns the document title
func (m *MOBIDocument) GetTitle() string {
	return m.title
}

// GetAuthor returns the document author
func (m *MOBIDocument) GetAuthor() string {
	return m.author
}

// GetPageCount returns the total number of pages
func (m *MOBIDocument) GetPageCount() int {
	return len(m.pages)
}

// GetCurrentPage returns the current page number
func (m *MOBIDocument) GetCurrentPage() int {
	return m.currentPage
}

// SetCurrentPage sets the current page
func (m *MOBIDocument) SetCurrentPage(page int) error {
	if page < 1 || page > len(m.pages) {
		return fmt.Errorf("page number %d out of range (1-%d)", page, len(m.pages))
	}
	m.currentPage = page
	return nil
}

// GetPageContent returns the page content as text
func (m *MOBIDocument) GetPageContent(page int) (interface{}, error) {
	if page < 1 || page > len(m.pages) {
		return nil, fmt.Errorf("page number %d out of range (1-%d)", page, len(m.pages))
	}

	return m.pages[page-1], nil
}

// GetType returns the document type
func (m *MOBIDocument) GetType() DocumentType {
	return TypeMOBI
}

// Close closes the MOBI document
func (m *MOBIDocument) Close() error {
	// Clean up resources
	m.pages = nil
	return nil
}
