package qtui

import (
	"fmt"
	"image"
	"path/filepath"
	"strings"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/gui"
	"github.com/therecipe/qt/widgets"

	"ebookreader/reader"
)

// MainWindow represents the main application window
type MainWindow struct {
	*widgets.QMainWindow
	
	// Document management
	docManager *reader.DocumentManager
	
	// UI Components
	centralWidget    *widgets.QWidget
	contentStack     *widgets.QStackedWidget
	
	// For PDF display
	pdfScrollArea    *widgets.QScrollArea
	pdfLabel         *widgets.QLabel
	
	// For text display (EPUB/MOBI)
	textScrollArea   *widgets.QScrollArea
	textEdit         *widgets.QTextEdit
	
	// Toolbar
	toolbar          *widgets.QToolBar
	openAction       *widgets.QAction
	prevAction       *widgets.QAction
	nextAction       *widgets.QAction
	firstAction      *widgets.QAction
	lastAction       *widgets.QAction
	
	// Status bar
	statusBar        *widgets.QStatusBar
	pageLabel        *widgets.QLabel
	documentInfo     *widgets.QLabel
	
	// Navigation
	pageSpinBox      *widgets.QSpinBox
	
	// Current state
	currentPage      int
}

// NewMainWindow creates a new main window
func NewMainWindow() *MainWindow {
	window := &MainWindow{
		QMainWindow: widgets.NewQMainWindow(nil, 0),
		docManager:  reader.NewDocumentManager(),
		currentPage: 1,
	}
	
	window.setupUI()
	window.setupConnections()
	window.setupMenus()
	window.updateUI()
	
	return window
}

// setupUI initializes the user interface
func (mw *MainWindow) setupUI() {
	// Set window properties
	mw.SetWindowTitle("Modern EBook Reader")
	mw.SetMinimumSize2(1000, 700)
	mw.Resize2(1200, 800)
	
	// Apply modern styling
	mw.setModernStyle()
	
	// Create central widget
	mw.centralWidget = widgets.NewQWidget(nil, 0)
	mw.SetCentralWidget(mw.centralWidget)
	
	// Create main layout
	mainLayout := widgets.NewQVBoxLayout()
	mw.centralWidget.SetLayout(mainLayout)
	
	// Create toolbar
	mw.createToolbar()
	
	// Create content stack (for switching between PDF and text views)
	mw.contentStack = widgets.NewQStackedWidget(nil)
	mainLayout.AddWidget(mw.contentStack, 1, 0)
	
	// Create PDF view
	mw.createPDFView()
	
	// Create text view
	mw.createTextView()
	
	// Create status bar
	mw.createStatusBar()
	
	// Set initial content
	mw.showWelcomeScreen()
}

// setModernStyle applies modern styling to the application
func (mw *MainWindow) setModernStyle() {
	styleSheet := `
		QMainWindow {
			background-color: #f5f5f5;
		}
		
		QToolBar {
			background-color: #ffffff;
			border: none;
			spacing: 8px;
			padding: 8px;
		}
		
		QToolBar QToolButton {
			background-color: #ffffff;
			border: 1px solid #ddd;
			border-radius: 6px;
			padding: 8px 12px;
			font-weight: 500;
		}
		
		QToolBar QToolButton:hover {
			background-color: #e3f2fd;
			border-color: #2196f3;
		}
		
		QToolBar QToolButton:pressed {
			background-color: #bbdefb;
		}
		
		QToolBar QToolButton:disabled {
			background-color: #f5f5f5;
			color: #ccc;
			border-color: #eee;
		}
		
		QStatusBar {
			background-color: #ffffff;
			border-top: 1px solid #ddd;
			padding: 4px;
		}
		
		QTextEdit {
			background-color: #ffffff;
			border: 1px solid #ddd;
			border-radius: 4px;
			font-family: "Segoe UI", Arial, sans-serif;
			font-size: 14px;
			line-height: 1.6;
			padding: 20px;
		}
		
		QLabel {
			color: #333;
		}
		
		QScrollArea {
			border: none;
			background-color: #ffffff;
		}
		
		QSpinBox {
			border: 1px solid #ddd;
			border-radius: 4px;
			padding: 4px 8px;
			font-size: 12px;
			background-color: #ffffff;
		}
	`
	mw.SetStyleSheet(styleSheet)
}

// createToolbar creates the application toolbar
func (mw *MainWindow) createToolbar() {
	mw.toolbar = widgets.NewQToolBar2("Main", nil)
	mw.AddToolBar2(core.Qt__TopToolBarArea, mw.toolbar)
	mw.toolbar.SetMovable(false)
	mw.toolbar.SetFloatable(false)
	
	// Open file action
	mw.openAction = mw.toolbar.AddAction("📁 Open")
	mw.openAction.SetToolTip("Open document (PDF, EPUB, MOBI)")
	
	mw.toolbar.AddSeparator()
	
	// Navigation actions
	mw.firstAction = mw.toolbar.AddAction("⏮️ First")
	mw.firstAction.SetToolTip("Go to first page")
	
	mw.prevAction = mw.toolbar.AddAction("◀️ Previous")
	mw.prevAction.SetToolTip("Go to previous page")
	
	// Page selector
	mw.toolbar.AddWidget(widgets.NewQLabel2("Page:", nil, 0))
	mw.pageSpinBox = widgets.NewQSpinBox(nil)
	mw.pageSpinBox.SetMinimum(1)
	mw.pageSpinBox.SetMaximum(1)
	mw.pageSpinBox.SetMinimumWidth(80)
	mw.toolbar.AddWidget(mw.pageSpinBox)
	
	mw.nextAction = mw.toolbar.AddAction("▶️ Next")
	mw.nextAction.SetToolTip("Go to next page")
	
	mw.lastAction = mw.toolbar.AddAction("⏭️ Last")
	mw.lastAction.SetToolTip("Go to last page")
	
	// Initially disable navigation
	mw.setNavigationEnabled(false)
}

// createPDFView creates the PDF viewing area
func (mw *MainWindow) createPDFView() {
	mw.pdfScrollArea = widgets.NewQScrollArea(nil)
	mw.pdfScrollArea.SetAlignment(core.Qt__AlignCenter)
	mw.pdfScrollArea.SetWidgetResizable(true)
	
	mw.pdfLabel = widgets.NewQLabel(nil, 0)
	mw.pdfLabel.SetAlignment(core.Qt__AlignCenter)
	mw.pdfLabel.SetScaledContents(true)
	
	mw.pdfScrollArea.SetWidget(mw.pdfLabel)
	mw.contentStack.AddWidget(mw.pdfScrollArea)
}

// createTextView creates the text viewing area
func (mw *MainWindow) createTextView() {
	mw.textScrollArea = widgets.NewQScrollArea(nil)
	mw.textScrollArea.SetWidgetResizable(true)
	
	mw.textEdit = widgets.NewQTextEdit(nil)
	mw.textEdit.SetReadOnly(true)
	mw.textEdit.SetVerticalScrollBarPolicy(core.Qt__ScrollBarAsNeeded)
	mw.textEdit.SetHorizontalScrollBarPolicy(core.Qt__ScrollBarAsNeeded)
	
	mw.textScrollArea.SetWidget(mw.textEdit)
	mw.contentStack.AddWidget(mw.textScrollArea)
}

// createStatusBar creates the status bar
func (mw *MainWindow) createStatusBar() {
	mw.statusBar = widgets.NewQStatusBar(nil)
	
	mw.documentInfo = widgets.NewQLabel2("Ready", nil, 0)
	mw.pageLabel = widgets.NewQLabel2("", nil, 0)
	
	mw.statusBar.AddWidget(mw.documentInfo, 1)
	mw.statusBar.AddPermanentWidget(mw.pageLabel, 0)
	
	mw.SetStatusBar(mw.statusBar)
}

// setupConnections connects signals to slots
func (mw *MainWindow) setupConnections() {
	// File operations
	mw.openAction.ConnectTriggered(func(bool) {
		mw.openDocument()
	})
	
	// Navigation
	mw.firstAction.ConnectTriggered(func(bool) {
		mw.goToFirstPage()
	})
	
	mw.prevAction.ConnectTriggered(func(bool) {
		mw.goToPreviousPage()
	})
	
	mw.nextAction.ConnectTriggered(func(bool) {
		mw.goToNextPage()
	})
	
	mw.lastAction.ConnectTriggered(func(bool) {
		mw.goToLastPage()
	})
	
	// Page spinner
	mw.pageSpinBox.ConnectValueChanged(func(int) {
		mw.goToPage(mw.pageSpinBox.Value())
	})
}

// setupMenus creates the application menus
func (mw *MainWindow) setupMenus() {
	menuBar := mw.MenuBar()
	
	// File menu
	fileMenu := menuBar.AddMenu2("&File")
	
	openAction := fileMenu.AddAction("&Open...")
	openAction.SetShortcut(gui.QKeySequence_FromString("Ctrl+O", gui.QKeySequence__NativeText))
	openAction.ConnectTriggered(func(bool) {
		mw.openDocument()
	})
	
	fileMenu.AddSeparator()
	
	exitAction := fileMenu.AddAction("E&xit")
	exitAction.SetShortcut(gui.QKeySequence_FromString("Ctrl+Q", gui.QKeySequence__NativeText))
	exitAction.ConnectTriggered(func(bool) {
		mw.Close()
	})
	
	// View menu
	viewMenu := menuBar.AddMenu2("&View")
	
	zoomInAction := viewMenu.AddAction("Zoom &In")
	zoomInAction.SetShortcut(gui.QKeySequence_FromString("Ctrl++", gui.QKeySequence__NativeText))
	zoomInAction.ConnectTriggered(func(bool) {
		mw.zoomIn()
	})
	
	zoomOutAction := viewMenu.AddAction("Zoom &Out")
	zoomOutAction.SetShortcut(gui.QKeySequence_FromString("Ctrl+-", gui.QKeySequence__NativeText))
	zoomOutAction.ConnectTriggered(func(bool) {
		mw.zoomOut()
	})
	
	// Help menu
	helpMenu := menuBar.AddMenu2("&Help")
	
	aboutAction := helpMenu.AddAction("&About")
	aboutAction.ConnectTriggered(func(bool) {
		mw.showAbout()
	})
}

// showWelcomeScreen displays the welcome screen
func (mw *MainWindow) showWelcomeScreen() {
	welcomeText := `
	<div style="text-align: center; padding: 40px; font-family: 'Segoe UI', Arial, sans-serif;">
		<h1 style="color: #2196f3; margin-bottom: 20px;">📚 Modern EBook Reader</h1>
		<p style="font-size: 18px; color: #666; margin-bottom: 30px;">
			A modern, cross-platform ebook reader supporting multiple formats
		</p>
		
		<div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
			<h3 style="color: #333; margin-bottom: 15px;">Supported Formats</h3>
			<div style="display: inline-block; text-align: left;">
				<p>📄 <strong>PDF</strong> - Portable Document Format</p>
				<p>📖 <strong>EPUB</strong> - Electronic Publication</p>
				<p>📱 <strong>MOBI</strong> - Mobipocket eBook</p>
			</div>
		</div>
		
		<p style="color: #888; margin-top: 30px;">
			Click <strong>📁 Open</strong> or drag and drop a file to get started
		</p>
	</div>
	`
	
	mw.textEdit.SetHtml(welcomeText)
	mw.contentStack.SetCurrentWidget(mw.textScrollArea)
}

// openDocument opens a file dialog to select a document
func (mw *MainWindow) openDocument() {
	supportedFormats := strings.Join(reader.GetSupportedFormats(), " ")
	filter := fmt.Sprintf("Supported Files (*%s);;All Files (*)", strings.ReplaceAll(supportedFormats, " ", " *"))
	
	filename := widgets.QFileDialog_GetOpenFileName(
		mw,
		"Open Document",
		"",
		filter,
		"",
		widgets.QFileDialog__ReadOnly,
	)
	
	if filename != "" {
		mw.loadDocument(filename)
	}
}

// loadDocument loads a document file
func (mw *MainWindow) loadDocument(filename string) {
	// Show loading status
	mw.documentInfo.SetText("Loading document...")
	
	// Load the document
	err := mw.docManager.LoadDocument(filename)
	if err != nil {
		mw.showError("Failed to load document", err.Error())
		mw.documentInfo.SetText("Ready")
		return
	}
	
	doc := mw.docManager.GetDocument()
	
	// Update window title
	baseName := filepath.Base(filename)
	title := doc.GetTitle()
	if title != "" && title != "PDF Document" && title != "EPUB Document" && title != "MOBI Document" {
		mw.SetWindowTitle(fmt.Sprintf("Modern EBook Reader - %s", title))
	} else {
		mw.SetWindowTitle(fmt.Sprintf("Modern EBook Reader - %s", baseName))
	}
	
	// Reset to first page
	mw.currentPage = 1
	doc.SetCurrentPage(1)
	
	// Update UI based on document type
	mw.updateForDocumentType()
	
	// Display the first page
	mw.displayCurrentPage()
	
	// Update navigation
	mw.updateUI()
}

// updateForDocumentType updates the UI based on the document type
func (mw *MainWindow) updateForDocumentType() {
	doc := mw.docManager.GetDocument()
	if doc == nil {
		return
	}
	
	switch doc.GetType() {
	case reader.TypePDF:
		mw.contentStack.SetCurrentWidget(mw.pdfScrollArea)
	case reader.TypeEPUB, reader.TypeMOBI:
		mw.contentStack.SetCurrentWidget(mw.textScrollArea)
	}
}

// displayCurrentPage displays the current page
func (mw *MainWindow) displayCurrentPage() {
	doc := mw.docManager.GetDocument()
	if doc == nil {
		return
	}
	
	content, err := doc.GetPageContent(mw.currentPage)
	if err != nil {
		mw.showError("Failed to display page", err.Error())
		return
	}
	
	switch doc.GetType() {
	case reader.TypePDF:
		if img, ok := content.(image.Image); ok {
			mw.displayPDFPage(img)
		}
	case reader.TypeEPUB, reader.TypeMOBI:
		if text, ok := content.(string); ok {
			mw.displayTextPage(text)
		}
	}
}

// displayPDFPage displays a PDF page as an image
func (mw *MainWindow) displayPDFPage(img image.Image) {
	// Convert image to QPixmap
	pixmap := imageToQPixmap(img)
	
	// Scale the image to fit the scroll area while maintaining aspect ratio
	scrollSize := mw.pdfScrollArea.Size()
	scaledPixmap := pixmap.Scaled2(
		scrollSize.Width()-20,
		scrollSize.Height()-20,
		core.Qt__KeepAspectRatio,
		core.Qt__SmoothTransformation,
	)
	
	mw.pdfLabel.SetPixmap(scaledPixmap)
}

// displayTextPage displays a text page
func (mw *MainWindow) displayTextPage(text string) {
	// Format text with proper styling
	formattedText := fmt.Sprintf(`
	<div style="font-family: 'Segoe UI', Georgia, serif; font-size: 14px; line-height: 1.8; color: #333; max-width: 800px; margin: 0 auto; padding: 40px;">
		%s
	</div>
	`, strings.ReplaceAll(text, "\n", "<br>"))
	
	mw.textEdit.SetHtml(formattedText)
	mw.textEdit.MoveCursor(gui.QTextCursor__Start, gui.QTextCursor__MoveAnchor)
}

// Navigation methods
func (mw *MainWindow) goToFirstPage() {
	mw.goToPage(1)
}

func (mw *MainWindow) goToPreviousPage() {
	if mw.currentPage > 1 {
		mw.goToPage(mw.currentPage - 1)
	}
}

func (mw *MainWindow) goToNextPage() {
	doc := mw.docManager.GetDocument()
	if doc != nil && mw.currentPage < doc.GetPageCount() {
		mw.goToPage(mw.currentPage + 1)
	}
}

func (mw *MainWindow) goToLastPage() {
	doc := mw.docManager.GetDocument()
	if doc != nil {
		mw.goToPage(doc.GetPageCount())
	}
}

func (mw *MainWindow) goToPage(page int) {
	doc := mw.docManager.GetDocument()
	if doc == nil {
		return
	}
	
	err := doc.SetCurrentPage(page)
	if err != nil {
		return
	}
	
	mw.currentPage = page
	mw.displayCurrentPage()
	mw.updateUI()
}

// Zoom methods (for text content)
func (mw *MainWindow) zoomIn() {
	if mw.contentStack.CurrentWidget().Pointer() == mw.textScrollArea.Pointer() {
		font := mw.textEdit.Font()
		size := font.PointSize()
		if size < 24 {
			font.SetPointSize(size + 1)
			mw.textEdit.SetFont(font)
		}
	}
}

func (mw *MainWindow) zoomOut() {
	if mw.contentStack.CurrentWidget().Pointer() == mw.textScrollArea.Pointer() {
		font := mw.textEdit.Font()
		size := font.PointSize()
		if size > 8 {
			font.SetPointSize(size - 1)
			mw.textEdit.SetFont(font)
		}
	}
}

// updateUI updates the user interface state
func (mw *MainWindow) updateUI() {
	doc := mw.docManager.GetDocument()
	
	if doc == nil {
		mw.setNavigationEnabled(false)
		mw.documentInfo.SetText("Ready")
		mw.pageLabel.SetText("")
		mw.pageSpinBox.SetMaximum(1)
		mw.pageSpinBox.SetValue(1)
		return
	}
	
	// Update document info
	info := fmt.Sprintf("%s", doc.GetTitle())
	if author := doc.GetAuthor(); author != "" {
		info += fmt.Sprintf(" by %s", author)
	}
	mw.documentInfo.SetText(info)
	
	// Update page info
	pageCount := doc.GetPageCount()
	mw.pageLabel.SetText(fmt.Sprintf("Page %d of %d", mw.currentPage, pageCount))
	
	// Update page spinner
	mw.pageSpinBox.SetMaximum(pageCount)
	mw.pageSpinBox.SetValue(mw.currentPage)
	
	// Update navigation buttons
	mw.setNavigationEnabled(true)
	mw.firstAction.SetEnabled(mw.currentPage > 1)
	mw.prevAction.SetEnabled(mw.currentPage > 1)
	mw.nextAction.SetEnabled(mw.currentPage < pageCount)
	mw.lastAction.SetEnabled(mw.currentPage < pageCount)
}

// setNavigationEnabled enables or disables navigation controls
func (mw *MainWindow) setNavigationEnabled(enabled bool) {
	mw.firstAction.SetEnabled(enabled)
	mw.prevAction.SetEnabled(enabled)
	mw.nextAction.SetEnabled(enabled)
	mw.lastAction.SetEnabled(enabled)
	mw.pageSpinBox.SetEnabled(enabled)
}

// showError displays an error message
func (mw *MainWindow) showError(title, message string) {
	widgets.QMessageBox_Critical(
		mw,
		title,
		message,
		widgets.QMessageBox__Ok,
		widgets.QMessageBox__Ok,
	)
}

// showAbout displays the about dialog
func (mw *MainWindow) showAbout() {
	about := `
	<h2>Modern EBook Reader</h2>
	<p>Version 2.0</p>
	<p>A modern, cross-platform ebook reader built with Go and Qt.</p>
	<p><strong>Supported Formats:</strong></p>
	<ul>
		<li>PDF - Portable Document Format</li>
		<li>EPUB - Electronic Publication</li>
		<li>MOBI - Mobipocket eBook</li>
	</ul>
	<p>Built with Go, Qt, and love ❤️</p>
	`
	
	widgets.QMessageBox_About(mw, "About Modern EBook Reader", about)
}

// Event handlers for drag and drop
func (mw *MainWindow) DragEnterEvent(event *gui.QDragEnterEvent) {
	if event.MimeData().HasUrls() {
		urls := event.MimeData().Urls()
		if len(urls) > 0 {
			filename := urls[0].ToLocalFile()
			if reader.IsSupportedFormat(filename) {
				event.AcceptProposedAction()
				return
			}
		}
	}
	// Just ignore the event instead of calling Ignore()
}

func (mw *MainWindow) DropEvent(event *gui.QDropEvent) {
	urls := event.MimeData().Urls()
	if len(urls) > 0 {
		filename := urls[0].ToLocalFile()
		if reader.IsSupportedFormat(filename) {
			mw.loadDocument(filename)
			event.AcceptProposedAction()
			return
		}
	}
	// Just ignore the event instead of calling Ignore()
}
