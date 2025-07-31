package modernui

import (
	"fmt"
	"image"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/canvas"

	"ebookreader/reader"
)

// ModernApplication represents the modernized application
type ModernApplication struct {
	App       fyne.App
	Window    fyne.Window
	docManager *reader.DocumentManager
	
	// UI components
	currentPage   int
	contentStack  *container.AppTabs
	
	// PDF display
	pdfImage      *canvas.Image
	pdfContainer  *container.Scroll
	
	// Text display
	textEdit      *widget.RichText
	textContainer *container.Scroll
	
	// Controls
	pageLabel     *widget.Label
	toolbar       *fyne.Container
	
	// Navigation
	prevButton    *widget.Button
	nextButton    *widget.Button
	firstButton   *widget.Button
	lastButton    *widget.Button
	openButton    *widget.Button
	pageEntry     *widget.Entry
	
	// Status
	statusBar     *fyne.Container
	documentInfo  *widget.Label
}

// NewModernApplication creates a new modern application instance
func NewModernApplication() *ModernApplication {
	myApp := app.NewWithID("com.ebookreader.modern")

	window := myApp.NewWindow("Modern EBook Reader")
	window.Resize(fyne.NewSize(1200, 800))
	window.CenterOnScreen()

	application := &ModernApplication{
		App:         myApp,
		Window:      window,
		docManager:  reader.NewDocumentManager(),
		currentPage: 1,
	}

	application.setupUI()
	application.setupTheme()
	return application
}

// setupUI initializes the modern user interface
func (ma *ModernApplication) setupUI() {
	// Create main toolbar
	ma.createToolbar()
	
	// Create content area with tabs
	ma.contentStack = container.NewAppTabs()
	
	// Create PDF view
	ma.createPDFView()
	
	// Create text view  
	ma.createTextView()
	
	// Create status bar
	ma.createStatusBar()
	
	// Create main layout
	content := container.NewBorder(
		ma.toolbar,    // top
		ma.statusBar,  // bottom
		nil,          // left
		nil,          // right
		ma.contentStack, // center
	)
	
	ma.Window.SetContent(content)
	
	// Show welcome
	ma.showWelcomeScreen()
	
	// Enable drag and drop
	ma.Window.SetOnDropped(ma.handleFileDrop)
}

// setupTheme applies modern theming
func (ma *ModernApplication) setupTheme() {
	// Set a modern app theme if available
	// Fyne handles theming automatically
}

// createToolbar creates the modern toolbar
func (ma *ModernApplication) createToolbar() {
	// File operations
	ma.openButton = widget.NewButtonWithIcon("Open", nil, ma.openDocument)
	ma.openButton.Importance = widget.HighImportance
	
	// Navigation buttons
	ma.firstButton = widget.NewButtonWithIcon("", nil, ma.goToFirstPage)
	ma.firstButton.SetText("⏮")
	
	ma.prevButton = widget.NewButtonWithIcon("", nil, ma.goToPreviousPage)
	ma.prevButton.SetText("◀")
	
	ma.nextButton = widget.NewButtonWithIcon("", nil, ma.goToNextPage)
	ma.nextButton.SetText("▶")
	
	ma.lastButton = widget.NewButtonWithIcon("", nil, ma.goToLastPage)
	ma.lastButton.SetText("⏭")
	
	// Page entry
	ma.pageEntry = widget.NewEntry()
	ma.pageEntry.SetText("1")
	ma.pageEntry.Resize(fyne.NewSize(60, 30))
	ma.pageEntry.OnSubmitted = func(text string) {
		ma.goToPageFromEntry()
	}
	
	ma.pageLabel = widget.NewLabel("of 0")
	
	// Arrange toolbar
	navSection := container.NewHBox(
		ma.firstButton,
		ma.prevButton,
		widget.NewLabel("Page:"),
		ma.pageEntry,
		ma.pageLabel,
		ma.nextButton,
		ma.lastButton,
	)
	
	ma.toolbar = container.NewVBox(
		container.NewHBox(ma.openButton, widget.NewSeparator(), navSection),
	)
	
	// Initially disable navigation
	ma.setNavigationEnabled(false)
}

// createPDFView creates the PDF viewing area
func (ma *ModernApplication) createPDFView() {
	// Create image container for PDF
	ma.pdfContainer = container.NewScroll(widget.NewCard("PDF Viewer", "PDF content will appear here", nil))
	
	// Add to tabs
	pdfTab := container.NewTabItem("📄 PDF", ma.pdfContainer)
	ma.contentStack.Append(pdfTab)
}

// createTextView creates the text viewing area
func (ma *ModernApplication) createTextView() {
	// Create rich text widget
	ma.textEdit = widget.NewRichTextFromMarkdown("")
	ma.textEdit.Wrapping = fyne.TextWrapWord
	
	ma.textContainer = container.NewScroll(ma.textEdit)
	
	// Add to tabs
	textTab := container.NewTabItem("📖 Text", ma.textContainer)
	ma.contentStack.Append(textTab)
}

// createStatusBar creates the status bar
func (ma *ModernApplication) createStatusBar() {
	ma.documentInfo = widget.NewLabel("Ready")
	
	progressInfo := widget.NewLabel("")
	
	ma.statusBar = container.NewHBox(
		ma.documentInfo,
		widget.NewSeparator(),
		progressInfo,
	)
}

// showWelcomeScreen displays the welcome screen
func (ma *ModernApplication) showWelcomeScreen() {
	welcomeContent := `
# 📚 Modern EBook Reader

Welcome to the Modern EBook Reader - a cross-platform application for reading digital books.

## ✨ Features

- **Multi-format Support**: PDF, EPUB, and MOBI files
- **Modern Interface**: Clean, intuitive design with tabbed viewing
- **Easy Navigation**: Page-by-page or continuous scrolling
- **Drag & Drop**: Simply drag files into the window
- **Offline Reading**: No internet connection required

## 🚀 Getting Started

1. **Open a Document**: Click the "Open" button or drag a file into this window
2. **Navigate**: Use the navigation buttons or type a page number
3. **Read**: Content adapts automatically to the format

## 📋 Supported Formats

- **📄 PDF** - High-quality page rendering
- **📖 EPUB** - Reflowable text with proper formatting  
- **📱 MOBI** - Kindle-compatible ebook format

---

*Drag and drop a file to begin reading!*
`

	ma.textEdit.ParseMarkdown(welcomeContent)
	// Update tab text
	if len(ma.contentStack.Items) > 1 {
		ma.contentStack.Items[1].Text = "📖 Welcome"
		ma.contentStack.SelectTab(ma.contentStack.Items[1])
	}
}

// openDocument opens a file dialog to select a document
func (ma *ModernApplication) openDocument() {
	dialog.ShowFileOpen(func(fileReader fyne.URIReadCloser, err error) {
		if err != nil {
			ma.showError("File Error", err.Error())
			return
		}
		if fileReader == nil {
			return // User cancelled
		}
		
		filename := fileReader.URI().Path()
		fileReader.Close()
		
		if !reader.IsSupportedFormat(filename) {
			ma.showError("Unsupported Format", "Please select a PDF, EPUB, or MOBI file")
			return
		}
		
		ma.loadDocument(filename)
	}, ma.Window)
}

// loadDocument loads a document file
func (ma *ModernApplication) loadDocument(filename string) {
	// Show loading status
	ma.documentInfo.SetText("Loading document...")
	
	// Load the document
	err := ma.docManager.LoadDocument(filename)
	if err != nil {
		ma.showError("Load Error", fmt.Sprintf("Failed to load document: %v", err))
		ma.documentInfo.SetText("Ready")
		return
	}
	
	doc := ma.docManager.GetDocument()
	
	// Update window title
	baseName := filepath.Base(filename)
	title := doc.GetTitle()
	if title != "" && !strings.Contains(title, "Document") {
		ma.Window.SetTitle(fmt.Sprintf("Modern EBook Reader - %s", title))
	} else {
		ma.Window.SetTitle(fmt.Sprintf("Modern EBook Reader - %s", baseName))
	}
	
	// Reset to first page
	ma.currentPage = 1
	doc.SetCurrentPage(1)
	
	// Switch to appropriate view
	ma.switchToDocumentView(doc.GetType())
	
	// Display the first page
	ma.displayCurrentPage()
	
	// Update UI state
	ma.updateUI()
}

// switchToDocumentView switches to the appropriate tab for the document type
func (ma *ModernApplication) switchToDocumentView(docType reader.DocumentType) {
	switch docType {
	case reader.TypePDF:
		if len(ma.contentStack.Items) > 0 {
			ma.contentStack.Items[0].Text = "📄 PDF"
			ma.contentStack.SelectTab(ma.contentStack.Items[0])
		}
	case reader.TypeEPUB, reader.TypeMOBI:
		formatName := "EPUB"
		if docType == reader.TypeMOBI {
			formatName = "MOBI"
		}
		if len(ma.contentStack.Items) > 1 {
			ma.contentStack.Items[1].Text = fmt.Sprintf("📖 %s", formatName)
			ma.contentStack.SelectTab(ma.contentStack.Items[1])
		}
	}
}

// displayCurrentPage displays the current page
func (ma *ModernApplication) displayCurrentPage() {
	doc := ma.docManager.GetDocument()
	if doc == nil {
		return
	}
	
	content, err := doc.GetPageContent(ma.currentPage)
	if err != nil {
		ma.showError("Display Error", fmt.Sprintf("Failed to display page: %v", err))
		return
	}
	
	switch doc.GetType() {
	case reader.TypePDF:
		if img, ok := content.(image.Image); ok {
			ma.displayPDFPage(img)
		}
	case reader.TypeEPUB, reader.TypeMOBI:
		if text, ok := content.(string); ok {
			ma.displayTextPage(text)
		}
	}
}

// displayPDFPage displays a PDF page
func (ma *ModernApplication) displayPDFPage(img image.Image) {
	if ma.pdfImage == nil {
		ma.pdfImage = canvas.NewImageFromImage(img)
		ma.pdfImage.FillMode = canvas.ImageFillContain
		ma.pdfContainer.Content = ma.pdfImage
	} else {
		ma.pdfImage.Image = img
		ma.pdfImage.Refresh()
	}
	ma.pdfContainer.Refresh()
}

// displayTextPage displays a text page
func (ma *ModernApplication) displayTextPage(text string) {
	// Format text as markdown for better rendering
	formattedText := strings.ReplaceAll(text, "\n\n", "\n\n")
	ma.textEdit.ParseMarkdown(formattedText)
	ma.textContainer.ScrollToTop()
}

// Navigation methods
func (ma *ModernApplication) goToFirstPage() {
	ma.goToPage(1)
}

func (ma *ModernApplication) goToPreviousPage() {
	if ma.currentPage > 1 {
		ma.goToPage(ma.currentPage - 1)
	}
}

func (ma *ModernApplication) goToNextPage() {
	doc := ma.docManager.GetDocument()
	if doc != nil && ma.currentPage < doc.GetPageCount() {
		ma.goToPage(ma.currentPage + 1)
	}
}

func (ma *ModernApplication) goToLastPage() {
	doc := ma.docManager.GetDocument()
	if doc != nil {
		ma.goToPage(doc.GetPageCount())
	}
}

func (ma *ModernApplication) goToPageFromEntry() {
	doc := ma.docManager.GetDocument()
	if doc == nil {
		return
	}
	
	// Parse page number from entry
	var page int
	fmt.Sscanf(ma.pageEntry.Text, "%d", &page)
	
	if page >= 1 && page <= doc.GetPageCount() {
		ma.goToPage(page)
	} else {
		ma.pageEntry.SetText(fmt.Sprintf("%d", ma.currentPage))
	}
}

func (ma *ModernApplication) goToPage(page int) {
	doc := ma.docManager.GetDocument()
	if doc == nil {
		return
	}
	
	err := doc.SetCurrentPage(page)
	if err != nil {
		return
	}
	
	ma.currentPage = page
	ma.displayCurrentPage()
	ma.updateUI()
}

// updateUI updates the user interface state
func (ma *ModernApplication) updateUI() {
	doc := ma.docManager.GetDocument()
	
	if doc == nil {
		ma.setNavigationEnabled(false)
		ma.documentInfo.SetText("Ready")
		ma.pageLabel.SetText("of 0")
		ma.pageEntry.SetText("1")
		return
	}
	
	// Update document info
	info := doc.GetTitle()
	if author := doc.GetAuthor(); author != "" {
		info += fmt.Sprintf(" by %s", author)
	}
	ma.documentInfo.SetText(info)
	
	// Update page info
	pageCount := doc.GetPageCount()
	ma.pageLabel.SetText(fmt.Sprintf("of %d", pageCount))
	ma.pageEntry.SetText(fmt.Sprintf("%d", ma.currentPage))
	
	// Update navigation buttons
	ma.setNavigationEnabled(true)
	ma.firstButton.Enable()
	ma.prevButton.Enable()
	ma.nextButton.Enable()
	ma.lastButton.Enable()
	
	if ma.currentPage <= 1 {
		ma.firstButton.Disable()
		ma.prevButton.Disable()
	}
	
	if ma.currentPage >= pageCount {
		ma.nextButton.Disable()
		ma.lastButton.Disable()
	}
}

// setNavigationEnabled enables or disables navigation controls
func (ma *ModernApplication) setNavigationEnabled(enabled bool) {
	if enabled {
		ma.firstButton.Enable()
		ma.prevButton.Enable()
		ma.nextButton.Enable()
		ma.lastButton.Enable()
		ma.pageEntry.Enable()
	} else {
		ma.firstButton.Disable()
		ma.prevButton.Disable()
		ma.nextButton.Disable()
		ma.lastButton.Disable()
		ma.pageEntry.Disable()
	}
}

// showError displays an error message
func (ma *ModernApplication) showError(title, message string) {
	dialog.ShowError(fmt.Errorf(message), ma.Window)
}

// handleFileDrop handles drag and drop of files
func (ma *ModernApplication) handleFileDrop(position fyne.Position, uris []fyne.URI) {
	if len(uris) == 0 {
		return
	}

	// Get the first file
	uri := uris[0]
	filename := uri.Path()

	// Check if it's a supported format
	if !reader.IsSupportedFormat(filename) {
		ma.showError("Unsupported Format", "Please drop a PDF, EPUB, or MOBI file")
		return
	}

	// Load the document
	ma.loadDocument(filename)
}

// Run starts the application
func (ma *ModernApplication) Run() {
	ma.Window.ShowAndRun()
}
