package modernui

import (
	"fmt"
	"image"
	"image/color"
	"path/filepath"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/driver/desktop"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"

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

	// Document display
	pdfImage      *canvas.Image
	pdfContainer  *container.Scroll
	enhancedViewer *EnhancedImageViewer

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

	// Zoom and view controls
	zoomInButton    *widget.Button
	zoomOutButton   *widget.Button
	fitPageButton   *widget.Button
	fitWidthButton  *widget.Button
	zoomLabel       *widget.Label
	helpButton      *widget.Button
	zoomModeButton  *widget.Button

	// Zoom state
	zoomLevel       float64
	fitMode         string // "page", "width", "custom"
	scrollZoomMode  bool   // Toggle between page navigation and zoom with scroll wheel

	// Status
	statusBar       *fyne.Container
	documentInfo    *widget.Label

	// Welcome tab management
	welcomeTabIndex int
	hasWelcomeTab   bool

	// Keyboard shortcuts
	shortcuts       map[string]func()
}

// ModernTheme implements a clean, minimal theme for the application
type ModernTheme struct{}

// Color returns theme colors with a modern, minimal palette
func (m ModernTheme) Color(name fyne.ThemeColorName, variant fyne.ThemeVariant) color.Color {
	switch name {
	case theme.ColorNameBackground:
		return color.RGBA{R: 250, G: 250, B: 250, A: 255} // Very light gray
	case theme.ColorNameButton:
		return color.RGBA{R: 245, G: 245, B: 245, A: 255} // Light gray
	case theme.ColorNameDisabledButton:
		return color.RGBA{R: 240, G: 240, B: 240, A: 255} // Lighter gray
	case theme.ColorNameForeground:
		return color.RGBA{R: 33, G: 33, B: 33, A: 255} // Dark gray text
	case theme.ColorNameHover:
		return color.RGBA{R: 240, G: 240, B: 240, A: 255} // Light hover
	case theme.ColorNameInputBackground:
		return color.RGBA{R: 255, G: 255, B: 255, A: 255} // Pure white
	case theme.ColorNamePrimary:
		return color.RGBA{R: 66, G: 133, B: 244, A: 255} // Subtle blue accent
	case theme.ColorNameFocus:
		return color.RGBA{R: 66, G: 133, B: 244, A: 100} // Subtle blue focus
	case theme.ColorNameSelection:
		return color.RGBA{R: 66, G: 133, B: 244, A: 50} // Very subtle selection
	case theme.ColorNameSeparator:
		return color.RGBA{R: 230, G: 230, B: 230, A: 255} // Light separator
	case theme.ColorNameShadow:
		return color.RGBA{R: 0, G: 0, B: 0, A: 20} // Very subtle shadow
	}
	return theme.DefaultTheme().Color(name, variant)
}

// Font returns clean, modern fonts
func (m ModernTheme) Font(style fyne.TextStyle) fyne.Resource {
	return theme.DefaultTheme().Font(style)
}

// Icon returns theme icons
func (m ModernTheme) Icon(name fyne.ThemeIconName) fyne.Resource {
	return theme.DefaultTheme().Icon(name)
}

// Size returns theme sizes with modern spacing
func (m ModernTheme) Size(name fyne.ThemeSizeName) float32 {
	switch name {
	case theme.SizeNamePadding:
		return 8 // Reduced padding for cleaner look
	case theme.SizeNameInlineIcon:
		return 16 // Smaller icons
	case theme.SizeNameScrollBar:
		return 8 // Thinner scrollbars
	case theme.SizeNameText:
		return theme.DefaultTheme().Size(name) // Use default text size
	}
	return theme.DefaultTheme().Size(name)
}

// NewModernApplication creates a new modern application instance
func NewModernApplication() *ModernApplication {
	myApp := app.NewWithID("com.ebookreader.modern")

	// Set the application icon for system integration
	myApp.SetIcon(resourceIconPng)

	window := myApp.NewWindow("Modern EBook Reader")
	window.Resize(fyne.NewSize(1400, 900))
	window.CenterOnScreen()

	// Set the window icon
	window.SetIcon(resourceIconPng)

	application := &ModernApplication{
		App:         myApp,
		Window:      window,
		docManager:  reader.NewDocumentManager(),
		currentPage:     1,
		zoomLevel:       1.0,
		fitMode:         "page",
		scrollZoomMode:  false, // Start with page navigation mode
		welcomeTabIndex: -1,    // No welcome tab initially
		hasWelcomeTab:   false,
		shortcuts:       make(map[string]func()),
	}

	application.setupTheme()
	application.setupUI()
	application.setupKeyboardShortcuts()
	return application
}

// setupTheme applies the modern minimal theme
func (ma *ModernApplication) setupTheme() {
	ma.App.Settings().SetTheme(&ModernTheme{})
}

// setupUI initializes the modern user interface
func (ma *ModernApplication) setupUI() {
	// Create main toolbar
	ma.createToolbar()

	// Create content area with tabs
	ma.contentStack = container.NewAppTabs()
	ma.contentStack.SetTabLocation(container.TabLocationTop)

	// Create document reader view
	ma.createReaderView()

	// Create text view
	ma.createTextView()

	// Create status bar
	ma.createStatusBar()

	// Create main layout with improved spacing
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

	// Setup mouse wheel handling
	ma.setupMouseHandling()
}



// createToolbar creates the modern toolbar
func (ma *ModernApplication) createToolbar() {
	// File operations
	ma.openButton = widget.NewButtonWithIcon("Open Document", theme.FolderOpenIcon(), ma.openDocument)
	ma.openButton.Importance = widget.HighImportance

	// Navigation buttons - icon only for minimal look
	ma.firstButton = widget.NewButtonWithIcon("", theme.MediaSkipPreviousIcon(), ma.goToFirstPage)
	ma.prevButton = widget.NewButtonWithIcon("", theme.NavigateBackIcon(), ma.goToPreviousPage)
	ma.nextButton = widget.NewButtonWithIcon("", theme.NavigateNextIcon(), ma.goToNextPage)
	ma.lastButton = widget.NewButtonWithIcon("", theme.MediaSkipNextIcon(), ma.goToLastPage)

	// Page entry with improved styling
	ma.pageEntry = widget.NewEntry()
	ma.pageEntry.SetText("1")
	ma.pageEntry.Resize(fyne.NewSize(70, 32))
	ma.pageEntry.OnSubmitted = func(text string) {
		ma.goToPageFromEntry()
	}
	ma.pageLabel = widget.NewLabel("of 0")

	// Zoom controls - icon only for minimal look
	ma.zoomInButton = widget.NewButtonWithIcon("", theme.ZoomInIcon(), ma.zoomIn)
	ma.zoomOutButton = widget.NewButtonWithIcon("", theme.ZoomOutIcon(), ma.zoomOut)
	ma.fitPageButton = widget.NewButton("Fit Page", ma.fitToPage)
	ma.fitWidthButton = widget.NewButton("Fit Width", ma.fitToWidth)
	ma.zoomLabel = widget.NewLabel("100%")

	// Zoom mode toggle button
	ma.zoomModeButton = widget.NewButton("Scroll: Pages", ma.toggleScrollZoomMode)

	// Help button - minimal
	ma.helpButton = widget.NewButtonWithIcon("Help", theme.HelpIcon(), ma.showHelp)

	// Arrange toolbar sections
	fileSection := container.NewHBox(ma.openButton)

	navSection := container.NewHBox(
		ma.firstButton,
		ma.prevButton,
		widget.NewLabel("Page:"),
		ma.pageEntry,
		ma.pageLabel,
		ma.nextButton,
		ma.lastButton,
	)

	zoomSection := container.NewHBox(
		ma.zoomOutButton,
		ma.zoomInButton,
		ma.zoomLabel,
		widget.NewSeparator(),
		ma.fitPageButton,
		ma.fitWidthButton,
		widget.NewSeparator(),
		ma.zoomModeButton,
	)

	helpSection := container.NewHBox(ma.helpButton)

	// Create main toolbar with sections
	ma.toolbar = container.NewVBox(
		container.NewBorder(
			nil, nil,
			fileSection,
			helpSection,
			container.NewHBox(
				widget.NewSeparator(),
				navSection,
				widget.NewSeparator(),
				zoomSection,
			),
		),
	)

	// Initially disable navigation and zoom
	ma.setNavigationEnabled(false)
	ma.setZoomEnabled(false)
}

// createReaderView creates the document reading area (renamed from createPDFView)
func (ma *ModernApplication) createReaderView() {
	// Create enhanced viewer for better mouse interaction
	ma.enhancedViewer = NewEnhancedImageViewer()

	// Set up callbacks for enhanced interactions
	ma.enhancedViewer.SetOnZoomChange(func(delta float64) {
		if delta == 0 {
			// Toggle zoom (double-click)
			if ma.fitMode == "page" {
				ma.setZoom(1.0)
			} else {
				ma.fitToPage()
			}
		} else {
			// Zoom with scroll wheel (when in zoom mode)
			if ma.scrollZoomMode {
				newZoom := ma.zoomLevel + delta
				ma.setZoom(newZoom)
			}
		}
	})

	ma.enhancedViewer.SetOnPageChange(func(delta int) {
		if delta > 0 {
			ma.goToNextPage()
		} else {
			ma.goToPreviousPage()
		}
	})

	// Set the zoom mode checker
	ma.enhancedViewer.SetGetZoomMode(func() bool {
		return ma.scrollZoomMode
	})

	// Get the scroll container from enhanced viewer
	ma.pdfContainer = ma.enhancedViewer.GetScrollContainer()

	// Add to tabs with minimal name
	readerTab := container.NewTabItem("Reader", ma.enhancedViewer)
	ma.contentStack.Append(readerTab)
}

// createTextView creates the text viewing area
func (ma *ModernApplication) createTextView() {
	// Create rich text widget with improved styling
	ma.textEdit = widget.NewRichTextFromMarkdown("")
	ma.textEdit.Wrapping = fyne.TextWrapWord

	ma.textContainer = container.NewScroll(ma.textEdit)

	// Add to tabs with minimal name
	textTab := container.NewTabItem("Text", ma.textContainer)
	ma.contentStack.Append(textTab)
}

// createStatusBar creates the status bar
func (ma *ModernApplication) createStatusBar() {
	ma.documentInfo = widget.NewLabel("Ready")

	// Create minimal status bar
	ma.statusBar = container.NewHBox(
		ma.documentInfo,
	)
}

// showWelcomeScreen displays the welcome screen
func (ma *ModernApplication) showWelcomeScreen() {
	// Only show welcome if no document is loaded and welcome tab doesn't exist
	if ma.hasWelcomeTab {
		return
	}

	// Create a container with the app icon and welcome text
	iconImage := canvas.NewImageFromResource(resourceIconPng)
	iconImage.FillMode = canvas.ImageFillOriginal
	iconImage.Resize(fyne.NewSize(96, 96))

	welcomeContent := `
# Modern EBook Reader

**Supported Formats:** PDF, EPUB, MOBI

**Quick Start:**
• Click "Open Document" or press Ctrl+O
• Drag and drop files onto the window
• Use F1 for complete help and shortcuts

**Features:**
• Clean, distraction-free reading
• Zoom controls and fit modes
• Keyboard shortcuts and mouse wheel navigation
• Professional document viewing
`

	// Create welcome text widget
	welcomeText := widget.NewRichTextFromMarkdown(welcomeContent)
	welcomeText.Wrapping = fyne.TextWrapWord

	// Create open button
	openButton := widget.NewButtonWithIcon("Open Document", theme.FolderOpenIcon(), ma.openDocument)
	openButton.Importance = widget.HighImportance

	// Create help button
	helpButton := widget.NewButtonWithIcon("Help", theme.HelpIcon(), ma.showHelp)

	buttonContainer := container.NewHBox(
		openButton,
		helpButton,
	)

	// Create main welcome container with minimal styling
	welcomeContainer := container.NewVBox(
		container.NewCenter(iconImage),
		welcomeText,
		container.NewCenter(buttonContainer),
	)

	// Create welcome tab
	welcomeTab := container.NewTabItem("Welcome", container.NewPadded(welcomeContainer))
	ma.contentStack.Append(welcomeTab)
	ma.welcomeTabIndex = len(ma.contentStack.Items) - 1
	ma.hasWelcomeTab = true

	// Select the welcome tab
	ma.contentStack.SelectTab(welcomeTab)
}

// closeWelcomeTab removes the welcome tab when a document is opened
func (ma *ModernApplication) closeWelcomeTab() {
	if !ma.hasWelcomeTab || ma.welcomeTabIndex < 0 {
		return
	}

	// Remove the welcome tab
	if ma.welcomeTabIndex < len(ma.contentStack.Items) {
		ma.contentStack.RemoveIndex(ma.welcomeTabIndex)
		ma.hasWelcomeTab = false
		ma.welcomeTabIndex = -1
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
	
	// Close welcome tab if it exists
	ma.closeWelcomeTab()

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
			ma.contentStack.Items[0].Text = "Reader"
			ma.contentStack.SelectTab(ma.contentStack.Items[0])
		}
	case reader.TypeEPUB, reader.TypeMOBI:
		if len(ma.contentStack.Items) > 1 {
			ma.contentStack.Items[1].Text = "Text"
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

// displayPDFPage displays a PDF page with zoom support
func (ma *ModernApplication) displayPDFPage(img image.Image) {
	if ma.pdfImage == nil {
		ma.pdfImage = canvas.NewImageFromImage(img)
	} else {
		ma.pdfImage.Image = img
		ma.pdfImage.Refresh()
	}

	// Apply zoom and fit mode
	ma.applyImageZoom()

	// Update the enhanced viewer
	ma.enhancedViewer.SetImage(ma.pdfImage)
}

// applyImageZoom applies the current zoom level and fit mode to the image
func (ma *ModernApplication) applyImageZoom() {
	if ma.pdfImage == nil {
		return
	}

	switch ma.fitMode {
	case "page":
		ma.pdfImage.FillMode = canvas.ImageFillContain
		ma.pdfImage.Resize(ma.pdfContainer.Size())
	case "width":
		ma.pdfImage.FillMode = canvas.ImageFillOriginal
		// Calculate size to fit width
		containerSize := ma.pdfContainer.Size()
		if containerSize.Width > 0 {
			ma.pdfImage.Resize(fyne.NewSize(containerSize.Width, 0))
		}
	case "custom":
		ma.pdfImage.FillMode = canvas.ImageFillOriginal
		// Apply custom zoom
		if ma.pdfImage.Image != nil {
			bounds := ma.pdfImage.Image.Bounds()
			originalWidth := float32(bounds.Dx())
			originalHeight := float32(bounds.Dy())

			newWidth := originalWidth * float32(ma.zoomLevel)
			newHeight := originalHeight * float32(ma.zoomLevel)

			ma.pdfImage.Resize(fyne.NewSize(newWidth, newHeight))
		}
	}
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
		ma.setZoomEnabled(false)
		ma.documentInfo.SetText("Ready - Press F1 for help")
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
	ma.setZoomEnabled(true)
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

	// Update zoom display
	ma.updateZoomDisplay()
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

// setupKeyboardShortcuts configures keyboard shortcuts
func (ma *ModernApplication) setupKeyboardShortcuts() {
	ma.shortcuts = map[string]func(){
		"F1":           ma.showHelp,
		"Ctrl+O":       ma.openDocument,
		"Left":         ma.goToPreviousPage,
		"Right":        ma.goToNextPage,
		"Home":         ma.goToFirstPage,
		"End":          ma.goToLastPage,
		"Page_Up":      ma.goToPreviousPage,
		"Page_Down":    ma.goToNextPage,
		"Ctrl+Plus":    ma.zoomIn,
		"Ctrl+Minus":   ma.zoomOut,
		"Ctrl+0":       func() { ma.setZoom(1.0) },
		"Ctrl+1":       ma.fitToPage,
		"Ctrl+2":       ma.fitToWidth,
		"Ctrl+Z":       ma.toggleScrollZoomMode,
	}

	// Set up actual Fyne keyboard shortcuts
	canvas := ma.Window.Canvas()

	// File operations
	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyF1,
	}, func(shortcut fyne.Shortcut) {
		ma.showHelp()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyO,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.openDocument()
	})

	// Navigation shortcuts
	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyLeft,
	}, func(shortcut fyne.Shortcut) {
		ma.goToPreviousPage()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyRight,
	}, func(shortcut fyne.Shortcut) {
		ma.goToNextPage()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyHome,
	}, func(shortcut fyne.Shortcut) {
		ma.goToFirstPage()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyEnd,
	}, func(shortcut fyne.Shortcut) {
		ma.goToLastPage()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyPageUp,
	}, func(shortcut fyne.Shortcut) {
		ma.goToPreviousPage()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyPageDown,
	}, func(shortcut fyne.Shortcut) {
		ma.goToNextPage()
	})

	// Zoom shortcuts
	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyEqual, // Plus key
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.zoomIn()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyMinus,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.zoomOut()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.Key0,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.setZoom(1.0)
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.Key1,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.fitToPage()
	})

	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.Key2,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.fitToWidth()
	})

	// Additional zoom shortcuts for better accessibility
	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyPlus,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.zoomIn()
	})

	// Toggle scroll zoom mode
	canvas.AddShortcut(&desktop.CustomShortcut{
		KeyName: fyne.KeyZ,
		Modifier: fyne.KeyModifierControl,
	}, func(shortcut fyne.Shortcut) {
		ma.toggleScrollZoomMode()
	})
}

// handleGlobalKeyEvent handles global key events for modifier tracking
func (ma *ModernApplication) handleGlobalKeyEvent(event *fyne.KeyEvent) {
	// This can be used for global key state tracking if needed
	// For now, we'll rely on the existing keyboard shortcuts
}

// setupMouseHandling configures mouse interactions
func (ma *ModernApplication) setupMouseHandling() {
	// Mouse interactions are handled automatically by Fyne:
	// - Mouse wheel scrolling (vertical and horizontal with Shift)
	// - Pan/drag functionality when content is zoomed
	// - Touch/trackpad gestures on supported platforms
	// Enhanced interactions are provided by the EnhancedImageViewer widget

	// Set up focus handling for the enhanced viewer to receive events
	if ma.enhancedViewer != nil {
		ma.Window.Canvas().SetOnTypedKey(func(event *fyne.KeyEvent) {
			// Handle global key events for modifier tracking
			ma.handleGlobalKeyEvent(event)
		})
	}
}

// showError displays an error message
func (ma *ModernApplication) showError(title, message string) {
	dialog.ShowError(fmt.Errorf("%s", message), ma.Window)
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

// showHelp displays the help dialog with keyboard shortcuts
func (ma *ModernApplication) showHelp() {
	helpContent := `# 📚 Modern EBook Reader - Complete Guide

## 🎯 Keyboard Shortcuts

### File Operations
- **Ctrl+O** - Open document dialog
- **F1** - Show this help guide

### Page Navigation
- **← (Left Arrow)** - Previous page
- **→ (Right Arrow)** - Next page
- **Page Up** - Previous page
- **Page Down** - Next page
- **Home** - Jump to first page
- **End** - Jump to last page

### Zoom & View Controls
- **Ctrl + +** - Zoom in (increase magnification)
- **Ctrl + -** - Zoom out (decrease magnification)
- **Ctrl + 0** - Reset zoom to 100%
- **Ctrl + 1** - Fit document to page
- **Ctrl + 2** - Fit document to width
- **Ctrl + Z** - Toggle mouse wheel mode (page navigation ↔ zoom)

## 🖱️ Mouse & Touch Controls

### Navigation
- **Mouse wheel** - Navigate pages OR zoom (toggle with Ctrl+Z)
- **Shift + Mouse wheel** - Horizontal scrolling when zoomed
- **Double-click** - Toggle between fit modes

### Document Interaction
- **Click and drag** - Pan around zoomed documents
- **Double-click** - Toggle between fit modes
- **Drag & drop files** - Open documents by dropping them into the window

## 🎛️ Toolbar Guide

### File Section
- **Open Document** - Browse and select files (PDF, EPUB, MOBI)

### Navigation Section
- **First/Last** - Jump to document boundaries
- **Prev/Next** - Navigate page by page
- **Page Entry** - Type page number and press Enter to jump

### Zoom Section
- **Zoom In/Out** - Adjust magnification level
- **Fit Page** - Scale to fit entire page in view
- **Fit Width** - Scale to fit page width
- **Zoom %** - Current zoom level indicator
- **Scroll Mode** - Toggle mouse wheel behavior (Pages/Zoom)

### Help Section
- **Help (F1)** - Open this help guide

## 📄 Supported File Formats

### PDF Documents
- High-quality page rendering
- Maintains original formatting and layout
- Supports zoom and navigation

### EPUB eBooks
- Reflowable text with proper formatting
- Adapts to different screen sizes
- Supports rich text and images

### MOBI eBooks
- Kindle-compatible format
- Optimized for reading devices
- Supports text formatting

## 💡 Pro Tips & Features

### Quick Access
- **Drag & Drop**: Simply drag files into the window to open them
- **Page Jumping**: Use the page entry field for quick navigation
- **Tab Switching**: Use Reader tab for images, Text View for reflowable content

### Status Information
- **Document Info**: Shows title and author in status bar
- **Zoom Level**: Current magnification and fit mode
- **Page Progress**: Current page of total pages

### Modern Interface
- **Clean Design**: Minimalist interface focuses on content
- **Responsive Layout**: Adapts to different window sizes
- **Intuitive Controls**: Standard shortcuts and familiar icons

## 🔧 Troubleshooting

### Common Issues
- **File won't open**: Ensure it's a supported format (PDF, EPUB, MOBI)
- **Zoom too small/large**: Use Ctrl+0 to reset or fit buttons
- **Navigation not working**: Make sure a document is loaded

### Performance Tips
- **Large PDFs**: Use fit modes for better performance
- **Memory usage**: Close and reopen for very large documents
- **Smooth scrolling**: Use mouse wheel for best experience

---

**Need more help?** This guide covers all available features. For additional support, check the application documentation or contact support.

*Press Escape, click Close, or click outside this dialog to return to reading.*`

	// Create help dialog with improved styling and icon
	helpText := widget.NewRichTextFromMarkdown(helpContent)
	helpText.Wrapping = fyne.TextWrapWord

	// Add icon to help dialog
	helpIcon := canvas.NewImageFromResource(resourceIconPng)
	helpIcon.FillMode = canvas.ImageFillOriginal
	helpIcon.Resize(fyne.NewSize(64, 64))

	helpContainer := container.NewVBox(
		container.NewCenter(helpIcon),
		widget.NewSeparator(),
		helpText,
	)

	helpScroll := container.NewScroll(helpContainer)
	helpScroll.Resize(fyne.NewSize(700, 600))

	// Create dialog with better sizing
	helpDialog := dialog.NewCustom("📚 Modern EBook Reader - Complete Help Guide", "Close", helpScroll, ma.Window)
	helpDialog.Resize(fyne.NewSize(750, 650))
	helpDialog.Show()
}

// showQuickHelp displays a compact help overlay with essential shortcuts
func (ma *ModernApplication) showQuickHelp() {
	quickHelpContent := `# 🚀 Quick Help - Essential Shortcuts

## Most Used Commands
- **F1** - Full help guide
- **Ctrl+O** - Open document
- **← →** - Previous/Next page
- **Ctrl + +/-** - Zoom in/out
- **Ctrl+1** - Fit to page
- **Home/End** - First/Last page

## Mouse Controls
- **Mouse wheel** - Navigate pages (default) or zoom (Ctrl+Z to toggle)
- **Drag & drop** - Open files
- **Double-click** - Toggle zoom modes

*Press F1 for complete help guide*`

	// Create compact help dialog with icon
	quickHelpText := widget.NewRichTextFromMarkdown(quickHelpContent)
	quickHelpText.Wrapping = fyne.TextWrapWord

	// Add small icon to quick help
	quickHelpIcon := canvas.NewImageFromResource(resourceIconPng)
	quickHelpIcon.FillMode = canvas.ImageFillOriginal
	quickHelpIcon.Resize(fyne.NewSize(48, 48))

	quickHelpContainer := container.NewVBox(
		container.NewCenter(quickHelpIcon),
		widget.NewSeparator(),
		quickHelpText,
	)

	quickHelpDialog := dialog.NewCustom("⚡ Quick Help", "Got it!", quickHelpContainer, ma.Window)
	quickHelpDialog.Resize(fyne.NewSize(400, 400))
	quickHelpDialog.Show()
}

// setZoomEnabled enables or disables zoom controls
func (ma *ModernApplication) setZoomEnabled(enabled bool) {
	if enabled {
		ma.zoomInButton.Enable()
		ma.zoomOutButton.Enable()
		ma.fitPageButton.Enable()
		ma.fitWidthButton.Enable()
		ma.zoomModeButton.Enable()
	} else {
		ma.zoomInButton.Disable()
		ma.zoomOutButton.Disable()
		ma.fitPageButton.Disable()
		ma.fitWidthButton.Disable()
		ma.zoomModeButton.Disable()
	}
}

// Zoom functionality
func (ma *ModernApplication) zoomIn() {
	ma.setZoom(ma.zoomLevel * 1.2)
}

func (ma *ModernApplication) zoomOut() {
	ma.setZoom(ma.zoomLevel / 1.2)
}

func (ma *ModernApplication) fitToPage() {
	ma.fitMode = "page"
	ma.zoomLevel = 1.0
	ma.updateZoomDisplay()
	ma.refreshCurrentPage()
}

func (ma *ModernApplication) fitToWidth() {
	ma.fitMode = "width"
	ma.zoomLevel = 1.0
	ma.updateZoomDisplay()
	ma.refreshCurrentPage()
}

func (ma *ModernApplication) setZoom(level float64) {
	if level < 0.1 {
		level = 0.1
	}
	if level > 5.0 {
		level = 5.0
	}

	ma.zoomLevel = level
	ma.fitMode = "custom"
	ma.updateZoomDisplay()
	ma.refreshCurrentPage()
}



func (ma *ModernApplication) updateZoomDisplay() {
	percentage := int(ma.zoomLevel * 100)
	ma.zoomLabel.SetText(fmt.Sprintf("%d%%", percentage))

	// Update status bar zoom info
	if len(ma.statusBar.Objects) >= 5 {
		if zoomLabel, ok := ma.statusBar.Objects[4].(*widget.Label); ok {
			zoomLabel.SetText(fmt.Sprintf("Zoom: %d%% (%s)", percentage, ma.fitMode))
		}
	}
}

func (ma *ModernApplication) refreshCurrentPage() {
	if ma.docManager.IsLoaded() {
		ma.displayCurrentPage()
	}
}

// toggleScrollZoomMode toggles between page navigation and zoom mode for mouse wheel
func (ma *ModernApplication) toggleScrollZoomMode() {
	ma.scrollZoomMode = !ma.scrollZoomMode

	// Update button text to reflect current mode
	if ma.scrollZoomMode {
		ma.zoomModeButton.SetText("Scroll: Zoom")
	} else {
		ma.zoomModeButton.SetText("Scroll: Pages")
	}

	// Update status bar to show current mode
	ma.updateScrollModeStatus()
}

// updateScrollModeStatus updates the status bar with current scroll mode
func (ma *ModernApplication) updateScrollModeStatus() {
	if len(ma.statusBar.Objects) > 0 {
		if statusLabel, ok := ma.statusBar.Objects[0].(*widget.Label); ok {
			if ma.scrollZoomMode {
				statusLabel.SetText("Mouse wheel: Zoom")
			} else {
				statusLabel.SetText("Mouse wheel: Pages")
			}
		}
	}
}

// Run starts the application
func (ma *ModernApplication) Run() {
	ma.Window.ShowAndRun()
}
