package reader

import (
	"archive/zip"
	"encoding/xml"
	"fmt"
	"html"
	"io"
	"path/filepath"
	"regexp"
	"strings"
)

// EPUBDocument represents an EPUB document
type EPUBDocument struct {
	zipReader   *zip.ReadCloser
	currentPage int
	pages       []string // Each page is a chapter/section
	title       string
	author      string
}

// OPF structures for parsing EPUB metadata
type OPF struct {
	XMLName  xml.Name `xml:"package"`
	Metadata Metadata `xml:"metadata"`
	Manifest Manifest `xml:"manifest"`
	Spine    Spine    `xml:"spine"`
}

type Metadata struct {
	Title   []string `xml:"title"`
	Creator []string `xml:"creator"`
}

type Manifest struct {
	Items []ManifestItem `xml:"item"`
}

type ManifestItem struct {
	ID        string `xml:"id,attr"`
	Href      string `xml:"href,attr"`
	MediaType string `xml:"media-type,attr"`
}

type Spine struct {
	Items []SpineItem `xml:"itemref"`
}

type SpineItem struct {
	IDRef string `xml:"idref,attr"`
}

// NewEPUBDocument creates a new EPUB document
func NewEPUBDocument(filename string) (*EPUBDocument, error) {
	zipReader, err := zip.OpenReader(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open EPUB file: %v", err)
	}

	epubDoc := &EPUBDocument{
		zipReader:   zipReader,
		currentPage: 1,
	}

	// Parse EPUB structure
	err = epubDoc.parseEPUB()
	if err != nil {
		zipReader.Close()
		return nil, fmt.Errorf("failed to parse EPUB: %v", err)
	}

	// Set default title if empty
	if epubDoc.title == "" {
		epubDoc.title = "EPUB Document"
	}

	return epubDoc, nil
}

// parseEPUB parses the EPUB structure and extracts content
func (e *EPUBDocument) parseEPUB() error {
	// Find and parse the OPF file
	opfPath, err := e.findOPFPath()
	if err != nil {
		return err
	}

	opf, err := e.parseOPF(opfPath)
	if err != nil {
		return err
	}

	// Extract metadata
	if len(opf.Metadata.Title) > 0 {
		e.title = opf.Metadata.Title[0]
	}
	if len(opf.Metadata.Creator) > 0 {
		e.author = strings.Join(opf.Metadata.Creator, ", ")
	}

	// Extract content based on spine order
	basePath := filepath.Dir(opfPath)
	e.pages = make([]string, 0)

	for _, spineItem := range opf.Spine.Items {
		// Find the manifest item
		var manifestItem *ManifestItem
		for _, item := range opf.Manifest.Items {
			if item.ID == spineItem.IDRef {
				manifestItem = &item
				break
			}
		}

		if manifestItem != nil && (manifestItem.MediaType == "application/xhtml+xml" || manifestItem.MediaType == "text/html") {
			contentPath := filepath.Join(basePath, manifestItem.Href)
			content, err := e.readFileFromZip(contentPath)
			if err != nil {
				continue // Skip problematic files
			}

			text := e.extractTextFromHTML(content)
			if strings.TrimSpace(text) != "" {
				e.pages = append(e.pages, text)
			}
		}
	}

	if len(e.pages) == 0 {
		return fmt.Errorf("no readable content found in EPUB")
	}

	return nil
}

// findOPFPath finds the path to the OPF file
func (e *EPUBDocument) findOPFPath() (string, error) {
	// Read container.xml
	containerContent, err := e.readFileFromZip("META-INF/container.xml")
	if err != nil {
		return "", fmt.Errorf("container.xml not found")
	}

	// Parse container.xml to find OPF path
	re := regexp.MustCompile(`full-path="([^"]+)"`)
	matches := re.FindStringSubmatch(containerContent)
	if len(matches) < 2 {
		return "", fmt.Errorf("OPF path not found in container.xml")
	}

	return matches[1], nil
}

// parseOPF parses the OPF file
func (e *EPUBDocument) parseOPF(opfPath string) (*OPF, error) {
	content, err := e.readFileFromZip(opfPath)
	if err != nil {
		return nil, err
	}

	var opf OPF
	err = xml.Unmarshal([]byte(content), &opf)
	if err != nil {
		return nil, fmt.Errorf("failed to parse OPF: %v", err)
	}

	return &opf, nil
}

// readFileFromZip reads a file from the ZIP archive
func (e *EPUBDocument) readFileFromZip(filename string) (string, error) {
	for _, file := range e.zipReader.File {
		if file.Name == filename {
			reader, err := file.Open()
			if err != nil {
				return "", err
			}
			defer reader.Close()

			content, err := io.ReadAll(reader)
			if err != nil {
				return "", err
			}

			return string(content), nil
		}
	}
	return "", fmt.Errorf("file not found: %s", filename)
}

// extractTextFromHTML extracts plain text from HTML content
func (e *EPUBDocument) extractTextFromHTML(htmlContent string) string {
	// Remove script and style elements
	re := regexp.MustCompile(`(?s)<(script|style)[^>]*>.*?</\1>`)
	htmlContent = re.ReplaceAllString(htmlContent, "")

	// Remove HTML tags
	re = regexp.MustCompile(`<[^>]*>`)
	text := re.ReplaceAllString(htmlContent, " ")

	// Decode HTML entities
	text = html.UnescapeString(text)

	// Clean up whitespace
	re = regexp.MustCompile(`\s+`)
	text = re.ReplaceAllString(text, " ")

	return strings.TrimSpace(text)
}

// GetTitle returns the document title
func (e *EPUBDocument) GetTitle() string {
	return e.title
}

// GetAuthor returns the document author
func (e *EPUBDocument) GetAuthor() string {
	return e.author
}

// GetPageCount returns the total number of pages (chapters)
func (e *EPUBDocument) GetPageCount() int {
	return len(e.pages)
}

// GetCurrentPage returns the current page number
func (e *EPUBDocument) GetCurrentPage() int {
	return e.currentPage
}

// SetCurrentPage sets the current page
func (e *EPUBDocument) SetCurrentPage(page int) error {
	if page < 1 || page > len(e.pages) {
		return fmt.Errorf("page number %d out of range (1-%d)", page, len(e.pages))
	}
	e.currentPage = page
	return nil
}

// GetPageContent returns the page content as text
func (e *EPUBDocument) GetPageContent(page int) (interface{}, error) {
	if page < 1 || page > len(e.pages) {
		return nil, fmt.Errorf("page number %d out of range (1-%d)", page, len(e.pages))
	}

	return e.pages[page-1], nil
}

// GetType returns the document type
func (e *EPUBDocument) GetType() DocumentType {
	return TypeEPUB
}

// Close closes the EPUB document
func (e *EPUBDocument) Close() error {
	if e.zipReader != nil {
		e.zipReader.Close()
		e.zipReader = nil
	}
	e.pages = nil
	return nil
}
