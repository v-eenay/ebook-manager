package pdf

import (
	"fmt"
	"image"

	"github.com/gen2brain/go-fitz"
)

// Reader handles PDF file operations
type Reader struct {
	document  *fitz.Document
	filename  string
	pageCount int
}

// NewReader creates a new PDF reader instance
func NewReader() *Reader {
	return &Reader{}
}

// LoadPDF loads a PDF file and returns basic information
func (r *Reader) LoadPDF(filename string) error {
	// Open the PDF document
	doc, err := fitz.New(filename)
	if err != nil {
		return fmt.Errorf("failed to open PDF file: %v", err)
	}

	r.document = doc
	r.filename = filename
	r.pageCount = doc.NumPage()

	return nil
}

// GetPageCount returns the total number of pages
func (r *Reader) GetPageCount() int {
	return r.pageCount
}

// GetFilename returns the loaded filename
func (r *Reader) GetFilename() string {
	return r.filename
}

// RenderPage renders a specific page to an image
func (r *Reader) RenderPage(pageNum int) (image.Image, error) {
	if r.document == nil {
		return nil, fmt.Errorf("no PDF loaded")
	}

	if pageNum < 1 || pageNum > r.pageCount {
		return nil, fmt.Errorf("page number %d out of range (1-%d)", pageNum, r.pageCount)
	}

	// Convert to zero-based index
	pageIndex := pageNum - 1

	// Render the page at a reasonable DPI (150 DPI for good quality)
	img, err := r.document.Image(pageIndex)
	if err != nil {
		return nil, fmt.Errorf("failed to render page %d: %v", pageNum, err)
	}

	return img, nil
}

// RenderPageToBytes renders a page and returns it as PNG bytes (not needed for Fyne)
func (r *Reader) RenderPageToBytes(pageNum int) ([]byte, error) {
	// For Fyne, we don't need this method as we can work directly with image.Image
	return nil, fmt.Errorf("method not implemented - use RenderPage instead")
}

// IsLoaded returns true if a PDF is currently loaded
func (r *Reader) IsLoaded() bool {
	return r.document != nil
}

// Close closes the PDF reader
func (r *Reader) Close() error {
	if r.document != nil {
		r.document.Close()
		r.document = nil
	}
	r.filename = ""
	r.pageCount = 0
	return nil
}
