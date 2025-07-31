package ui

import (
	"fmt"
	"image"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/storage"
	"fyne.io/fyne/v2/widget"
	fyneApp "fyne.io/fyne/v2/app"
	fyneWindow "fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"

	"ebookreader/pdf"
)

// MainWindow represents the main application window
type MainWindow struct {
	*widgets.QMainWindow
	pdfReader    *pdf.Reader
	currentPage  int
	pdfLabel     *widgets.QLabel
	scrollArea   *widgets.QScrollArea
	statusBar    *widgets.QStatusBar
	pageLabel    *widgets.QLabel
	prevButton   *widgets.QPushButton
	nextButton   *widgets.QPushButton
	openButton   *widgets.QPushButton
}

// NewMainWindow creates and returns a new main window
func NewMainWindow() *MainWindow {
	window := &MainWindow{
		QMainWindow: widgets.NewQMainWindow(nil, 0),
		pdfReader:   pdf.NewReader(),
		currentPage: 1,
	}

	window.setupUI()
	window.setupConnections()
	
	return window
}

// setupUI initializes the user interface components
func (mw *MainWindow) setupUI() {
	// Set window properties
	mw.SetWindowTitle("EBook Reader")
	mw.SetMinimumSize2(800, 600)
	mw.Resize2(1000, 800)

	// Create central widget
	centralWidget := widgets.NewQWidget(nil, 0)
	mw.SetCentralWidget(centralWidget)

	// Create main layout
	mainLayout := widgets.NewQVBoxLayout()
	centralWidget.SetLayout(mainLayout)

	// Create toolbar
	toolbar := mw.createToolbar()
	mainLayout.AddWidget(toolbar, 0, 0)

	// Create scroll area for PDF display
	mw.scrollArea = widgets.NewQScrollArea(nil)
	mw.scrollArea.SetAlignment(core.Qt__AlignCenter)
	mw.scrollArea.SetWidgetResizable(true)

	// Create label for PDF content
	mw.pdfLabel = widgets.NewQLabel(nil, 0)
	mw.pdfLabel.SetAlignment(core.Qt__AlignCenter)
	mw.pdfLabel.SetText("Drop a PDF file here or click 'Open PDF' to get started")
	mw.pdfLabel.SetStyleSheet("QLabel { background-color: #f0f0f0; border: 2px dashed #aaa; padding: 50px; }")
	mw.pdfLabel.SetMinimumSize2(600, 400)

	mw.scrollArea.SetWidget(mw.pdfLabel)
	mainLayout.AddWidget(mw.scrollArea, 1, 0)

	// Create status bar
	mw.statusBar = widgets.NewQStatusBar(nil)
	mw.pageLabel = widgets.NewQLabel2("Ready", nil, 0)
	mw.statusBar.AddWidget(mw.pageLabel, 0)
	mw.SetStatusBar(mw.statusBar)

	// Enable drag and drop
	mw.SetAcceptDrops(true)
}

// createToolbar creates and returns the application toolbar
func (mw *MainWindow) createToolbar() *widgets.QWidget {
	toolbar := widgets.NewQWidget(nil, 0)
	layout := widgets.NewQHBoxLayout()
	toolbar.SetLayout(layout)

	// Open PDF button
	mw.openButton = widgets.NewQPushButton2("Open PDF", nil)
	mw.openButton.SetIcon(gui.NewQIcon5("://icons/open.png"))
	layout.AddWidget(mw.openButton, 0, 0)

	// Add spacing
	layout.AddStretch(0)

	// Previous page button
	mw.prevButton = widgets.NewQPushButton2("Previous", nil)
	mw.prevButton.SetEnabled(false)
	layout.AddWidget(mw.prevButton, 0, 0)

	// Next page button
	mw.nextButton = widgets.NewQPushButton2("Next", nil)
	mw.nextButton.SetEnabled(false)
	layout.AddWidget(mw.nextButton, 0, 0)

	return toolbar
}

// setupConnections connects signals to slots
func (mw *MainWindow) setupConnections() {
	// Open PDF button
	mw.openButton.ConnectClicked(func(bool) {
		mw.openPDFDialog()
	})

	// Navigation buttons
	mw.prevButton.ConnectClicked(func(bool) {
		mw.previousPage()
	})

	mw.nextButton.ConnectClicked(func(bool) {
		mw.nextPage()
	})
}

// openPDFDialog opens a file dialog to select a PDF
func (mw *MainWindow) openPDFDialog() {
	filename := widgets.QFileDialog_GetOpenFileName(
		mw,
		"Open PDF File",
		"",
		"PDF Files (*.pdf);;All Files (*)",
		"",
		widgets.QFileDialog__ReadOnly,
	)

	if filename != "" {
		mw.loadPDF(filename)
	}
}

// loadPDF loads and displays a PDF file
func (mw *MainWindow) loadPDF(filename string) {
	// Update status
	mw.statusBar.ShowMessage("Loading PDF...", 0)
	
	// Load the PDF
	err := mw.pdfReader.LoadPDF(filename)
	if err != nil {
		mw.showError(fmt.Sprintf("Failed to load PDF: %v", err))
		return
	}

	// Reset to first page
	mw.currentPage = 1
	
	// Update window title
	baseName := filepath.Base(filename)
	mw.SetWindowTitle(fmt.Sprintf("EBook Reader - %s", baseName))

	// Enable navigation buttons
	mw.updateNavigationButtons()

	// Display the first page
	mw.displayCurrentPage()
	
	// Update status
	mw.updateStatus()
}

// displayCurrentPage renders and displays the current page
func (mw *MainWindow) displayCurrentPage() {
	if !mw.pdfReader.IsLoaded() {
		return
	}

	// Update status
	mw.statusBar.ShowMessage("Rendering page...", 0)

	// Render the page
	pageBytes, err := mw.pdfReader.RenderPageToBytes(mw.currentPage)
	if err != nil {
		mw.showError(fmt.Sprintf("Failed to render page: %v", err))
		return
	}

	// Load image from bytes
	pixmap := gui.NewQPixmap()
	pixmap.LoadFromData(pageBytes, len(pageBytes), "PNG")

	// Scale image to fit the label while maintaining aspect ratio
	scaledPixmap := pixmap.Scaled2(
		mw.scrollArea.Width()-20,
		mw.scrollArea.Height()-20,
		core.Qt__KeepAspectRatio,
		core.Qt__SmoothTransformation,
	)

	// Set the image
	mw.pdfLabel.SetPixmap(scaledPixmap)
	mw.pdfLabel.SetStyleSheet("") // Remove placeholder styling

	// Update status and navigation
	mw.updateStatus()
	mw.updateNavigationButtons()
}

// previousPage navigates to the previous page
func (mw *MainWindow) previousPage() {
	if mw.currentPage > 1 {
		mw.currentPage--
		mw.displayCurrentPage()
	}
}

// nextPage navigates to the next page
func (mw *MainWindow) nextPage() {
	if mw.currentPage < mw.pdfReader.GetPageCount() {
		mw.currentPage++
		mw.displayCurrentPage()
	}
}

// updateNavigationButtons updates the state of navigation buttons
func (mw *MainWindow) updateNavigationButtons() {
	if !mw.pdfReader.IsLoaded() {
		mw.prevButton.SetEnabled(false)
		mw.nextButton.SetEnabled(false)
		return
	}

	pageCount := mw.pdfReader.GetPageCount()
	mw.prevButton.SetEnabled(mw.currentPage > 1)
	mw.nextButton.SetEnabled(mw.currentPage < pageCount)
}

// updateStatus updates the status bar with current page information
func (mw *MainWindow) updateStatus() {
	if !mw.pdfReader.IsLoaded() {
		mw.pageLabel.SetText("Ready")
		mw.statusBar.ClearMessage()
		return
	}

	pageCount := mw.pdfReader.GetPageCount()
	mw.pageLabel.SetText(fmt.Sprintf("Page %d of %d", mw.currentPage, pageCount))
	mw.statusBar.ClearMessage()
}

// showError displays an error message to the user
func (mw *MainWindow) showError(message string) {
	widgets.QMessageBox_Critical(
		mw,
		"Error",
		message,
		widgets.QMessageBox__Ok,
		widgets.QMessageBox__Ok,
	)
	mw.statusBar.ShowMessage("Error occurred", 5000)
}

// Event handlers for drag and drop

// DragEnterEvent handles drag enter events
func (mw *MainWindow) DragEnterEvent(event *gui.QDragEnterEvent) {
	if event.MimeData().HasUrls() {
		urls := event.MimeData().Urls()
		if len(urls) > 0 {
			filename := urls[0].ToLocalFile()
			if strings.ToLower(filepath.Ext(filename)) == ".pdf" {
				event.AcceptProposedAction()
				return
			}
		}
	}
	event.Ignore()
}

// DropEvent handles drop events
func (mw *MainWindow) DropEvent(event *gui.QDropEvent) {
	urls := event.MimeData().Urls()
	if len(urls) > 0 {
		filename := urls[0].ToLocalFile()
		if strings.ToLower(filepath.Ext(filename)) == ".pdf" {
			mw.loadPDF(filename)
			event.AcceptProposedAction()
			return
		}
	}
	event.Ignore()
}
