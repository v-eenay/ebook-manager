package ui

import (
	"fmt"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2"

	"ebookreader/pdf"
)

// Application represents the main application
type Application struct {
	App       fyne.App
	Window    fyne.Window
	pdfReader *pdf.Reader
	
	// UI components
	currentPage   int
	pdfImage      *canvas.Image
	pageLabel     *widget.Label
	prevButton    *widget.Button
	nextButton    *widget.Button
	openButton    *widget.Button
	scrollContainer *container.Scroll
}

// NewApplication creates and returns a new application instance
func NewApplication() *Application {
	myApp := app.New()

	window := myApp.NewWindow("EBook Reader")
	window.Resize(fyne.NewSize(1000, 800))

	application := &Application{
		App:         myApp,
		Window:      window,
		pdfReader:   pdf.NewReader(),
		currentPage: 1,
	}

	application.setupUI()
	return application
}

// setupUI initializes the user interface
func (a *Application) setupUI() {
	// Create buttons
	a.openButton = widget.NewButton("Open PDF", a.openPDFDialog)
	a.prevButton = widget.NewButton("Previous", a.previousPage)
	a.nextButton = widget.NewButton("Next", a.nextPage)
	
	// Initially disable navigation buttons
	a.prevButton.Disable()
	a.nextButton.Disable()

	// Create toolbar
	toolbar := container.NewHBox(
		a.openButton,
		widget.NewSeparator(),
		a.prevButton,
		a.nextButton,
	)

	// Create page label
	a.pageLabel = widget.NewLabel("Ready")

	// Create placeholder for PDF content
	placeholderText := widget.NewRichTextFromMarkdown(`
# EBook Reader

Drop a PDF file here or click **Open PDF** to get started.

---

**Supported Features:**
- Open PDF files
- Navigate between pages  
- Drag and drop support
- Offline functionality
`)
	placeholderText.Wrapping = fyne.TextWrapWord

	// Create scroll container for PDF content
	a.scrollContainer = container.NewScroll(placeholderText)
	a.scrollContainer.SetMinSize(fyne.NewSize(600, 400))

	// Create status bar
	statusBar := container.NewHBox(
		a.pageLabel,
		widget.NewSeparator(),
	)

	// Create main layout
	content := container.NewBorder(
		toolbar,        // top
		statusBar,      // bottom
		nil,           // left
		nil,           // right
		a.scrollContainer, // center
	)

	a.Window.SetContent(content)

	// Enable drag and drop
	a.Window.SetOnDropped(a.handleFileDrop)
}

// openPDFDialog opens a file dialog to select a PDF
func (a *Application) openPDFDialog() {
	dialog.ShowFileOpen(func(reader fyne.URIReadCloser, err error) {
		if err != nil {
			a.showError("File selection error", err.Error())
			return
		}
		if reader == nil {
			return // User cancelled
		}
		
		filename := reader.URI().Path()
		reader.Close()
		
		if strings.ToLower(filepath.Ext(filename)) != ".pdf" {
			a.showError("Invalid file", "Please select a PDF file")
			return
		}
		
		a.loadPDF(filename)
	}, a.Window)
}

// loadPDF loads and displays a PDF file
func (a *Application) loadPDF(filename string) {
	// Update page label
	a.pageLabel.SetText("Loading PDF...")

	// Load the PDF
	err := a.pdfReader.LoadPDF(filename)
	if err != nil {
		a.showError("PDF Loading Error", fmt.Sprintf("Failed to load PDF: %v", err))
		a.pageLabel.SetText("Ready")
		return
	}

	// Reset to first page
	a.currentPage = 1

	// Update window title
	baseName := filepath.Base(filename)
	a.Window.SetTitle(fmt.Sprintf("EBook Reader - %s", baseName))

	// Display the first page
	a.displayCurrentPage()

	// Enable navigation buttons
	a.updateNavigationButtons()
}

// displayCurrentPage renders and displays the current page
func (a *Application) displayCurrentPage() {
	if !a.pdfReader.IsLoaded() {
		return
	}

	// Update page label
	a.pageLabel.SetText("Rendering page...")

	// Render the page to an image
	img, err := a.pdfReader.RenderPage(a.currentPage)
	if err != nil {
		a.showError("Rendering Error", fmt.Sprintf("Failed to render page: %v", err))
		return
	}

	// Create a canvas image from the rendered image
	if a.pdfImage == nil {
		a.pdfImage = canvas.NewImageFromImage(img)
		a.pdfImage.FillMode = canvas.ImageFillContain
		a.pdfImage.SetMinSize(fyne.NewSize(600, 800))
		
		// Replace the content of the scroll container
		a.scrollContainer.Content = a.pdfImage
		a.scrollContainer.Refresh()
	} else {
		a.pdfImage.Image = img
		a.pdfImage.Refresh()
	}

	// Update status and navigation
	a.updateStatus()
	a.updateNavigationButtons()
}

// previousPage navigates to the previous page
func (a *Application) previousPage() {
	if a.currentPage > 1 {
		a.currentPage--
		a.displayCurrentPage()
	}
}

// nextPage navigates to the next page
func (a *Application) nextPage() {
	if a.currentPage < a.pdfReader.GetPageCount() {
		a.currentPage++
		a.displayCurrentPage()
	}
}

// updateNavigationButtons updates the state of navigation buttons
func (a *Application) updateNavigationButtons() {
	if !a.pdfReader.IsLoaded() {
		a.prevButton.Disable()
		a.nextButton.Disable()
		return
	}

	pageCount := a.pdfReader.GetPageCount()
	
	if a.currentPage > 1 {
		a.prevButton.Enable()
	} else {
		a.prevButton.Disable()
	}
	
	if a.currentPage < pageCount {
		a.nextButton.Enable()
	} else {
		a.nextButton.Disable()
	}
}

// updateStatus updates the status bar with current page information
func (a *Application) updateStatus() {
	if !a.pdfReader.IsLoaded() {
		a.pageLabel.SetText("Ready")
		return
	}

	pageCount := a.pdfReader.GetPageCount()
	a.pageLabel.SetText(fmt.Sprintf("Page %d of %d", a.currentPage, pageCount))
}

// showError displays an error message to the user
func (a *Application) showError(title, message string) {
	dialog.ShowError(fmt.Errorf(message), a.Window)
}

// handleFileDrop handles drag and drop of files
func (a *Application) handleFileDrop(position fyne.Position, uris []fyne.URI) {
	if len(uris) == 0 {
		return
	}

	// Get the first file
	uri := uris[0]
	filename := uri.Path()

	// Check if it's a PDF
	if strings.ToLower(filepath.Ext(filename)) != ".pdf" {
		a.showError("Invalid file", "Please drop a PDF file")
		return
	}

	// Load the PDF
	a.loadPDF(filename)
}

// Run starts the application
func (a *Application) Run() {
	a.Window.ShowAndRun()
}
