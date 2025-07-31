package reader

import (
	"fmt"

	"github.com/gen2brain/go-fitz"
)

// PDFDocument represents a PDF document
type PDFDocument struct {
	document    *fitz.Document
	currentPage int
	pageCount   int
	title       string
	author      string
}

// NewPDFDocument creates a new PDF document
func NewPDFDocument(filename string) (*PDFDocument, error) {
	doc, err := fitz.New(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open PDF file: %v", err)
	}

	pdf := &PDFDocument{
		document:    doc,
		currentPage: 1,
		pageCount:   doc.NumPage(),
	}

	// Try to get metadata
	metadata := doc.Metadata()
	if metadata != nil {
		pdf.title = metadata["title"]
		pdf.author = metadata["author"]
	}

	// Set default title if empty
	if pdf.title == "" {
		pdf.title = "PDF Document"
	}

	return pdf, nil
}

// GetTitle returns the document title
func (p *PDFDocument) GetTitle() string {
	return p.title
}

// GetAuthor returns the document author
func (p *PDFDocument) GetAuthor() string {
	return p.author
}

// GetPageCount returns the total number of pages
func (p *PDFDocument) GetPageCount() int {
	return p.pageCount
}

// GetCurrentPage returns the current page number
func (p *PDFDocument) GetCurrentPage() int {
	return p.currentPage
}

// SetCurrentPage sets the current page
func (p *PDFDocument) SetCurrentPage(page int) error {
	if page < 1 || page > p.pageCount {
		return fmt.Errorf("page number %d out of range (1-%d)", page, p.pageCount)
	}
	p.currentPage = page
	return nil
}

// GetPageContent returns the page content as an image
func (p *PDFDocument) GetPageContent(page int) (interface{}, error) {
	if page < 1 || page > p.pageCount {
		return nil, fmt.Errorf("page number %d out of range (1-%d)", page, p.pageCount)
	}

	// Convert to zero-based index
	pageIndex := page - 1

	// Render the page
	img, err := p.document.Image(pageIndex)
	if err != nil {
		return nil, fmt.Errorf("failed to render page %d: %v", page, err)
	}

	return img, nil
}

// GetType returns the document type
func (p *PDFDocument) GetType() DocumentType {
	return TypePDF
}

// Close closes the PDF document
func (p *PDFDocument) Close() error {
	if p.document != nil {
		p.document.Close()
		p.document = nil
	}
	return nil
}
