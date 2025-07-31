package reader

import (
	"fmt"
	"path/filepath"
	"strings"
)

// DocumentType represents the type of document
type DocumentType int

const (
	TypePDF DocumentType = iota
	TypeEPUB
	TypeMOBI
)

// Document represents a generic document interface
type Document interface {
	GetTitle() string
	GetAuthor() string
	GetPageCount() int
	GetCurrentPage() int
	SetCurrentPage(page int) error
	GetPageContent(page int) (interface{}, error) // Returns image.Image for PDF, string for EPUB/MOBI
	GetType() DocumentType
	Close() error
}

// DocumentManager handles different document types
type DocumentManager struct {
	document Document
	filename string
}

// NewDocumentManager creates a new document manager
func NewDocumentManager() *DocumentManager {
	return &DocumentManager{}
}

// LoadDocument loads a document based on its file extension
func (dm *DocumentManager) LoadDocument(filename string) error {
	ext := strings.ToLower(filepath.Ext(filename))
	
	var doc Document
	var err error
	
	switch ext {
	case ".pdf":
		doc, err = NewPDFDocument(filename)
	case ".epub":
		doc, err = NewEPUBDocument(filename)
	case ".mobi":
		doc, err = NewMOBIDocument(filename)
	default:
		return fmt.Errorf("unsupported file format: %s", ext)
	}
	
	if err != nil {
		return err
	}
	
	dm.document = doc
	dm.filename = filename
	return nil
}

// GetDocument returns the current document
func (dm *DocumentManager) GetDocument() Document {
	return dm.document
}

// GetFilename returns the current filename
func (dm *DocumentManager) GetFilename() string {
	return dm.filename
}

// IsLoaded returns true if a document is loaded
func (dm *DocumentManager) IsLoaded() bool {
	return dm.document != nil
}

// Close closes the current document
func (dm *DocumentManager) Close() error {
	if dm.document != nil {
		err := dm.document.Close()
		dm.document = nil
		dm.filename = ""
		return err
	}
	return nil
}

// GetSupportedFormats returns a list of supported file formats
func GetSupportedFormats() []string {
	return []string{".pdf", ".epub", ".mobi"}
}

// IsSupportedFormat checks if a file extension is supported
func IsSupportedFormat(filename string) bool {
	ext := strings.ToLower(filepath.Ext(filename))
	supported := GetSupportedFormats()
	
	for _, format := range supported {
		if ext == format {
			return true
		}
	}
	return false
}
