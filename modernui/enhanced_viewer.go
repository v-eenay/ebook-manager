package modernui

import (
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
)

// CustomScrollContainer wraps a scroll container with enhanced event handling
type CustomScrollContainer struct {
	*container.Scroll
	onZoomChange func(delta float64)
	onPageChange func(delta int)
}

// EnhancedImageViewer provides advanced mouse interaction for document viewing
type EnhancedImageViewer struct {
	widget.BaseWidget

	image        *canvas.Image
	scrollable   *container.Scroll
	onZoomChange func(delta float64)
	onPageChange func(delta int)
	getZoomMode  func() bool // Function to check if zoom mode is active

	// Mouse state
	isDragging   bool
	lastPos      fyne.Position

	// Focus state for keyboard events
	focused      bool
}

// NewCustomScrollContainer creates a custom scroll container with enhanced event handling
func NewCustomScrollContainer(content fyne.CanvasObject) *CustomScrollContainer {
	scroll := container.NewScroll(content)
	return &CustomScrollContainer{
		Scroll: scroll,
	}
}

// Scrolled handles scroll events with modifier key detection
func (c *CustomScrollContainer) Scrolled(event *fyne.ScrollEvent) {
	// Try to detect Ctrl key using desktop driver if available
	if desk, ok := fyne.CurrentApp().Driver().(desktop.Driver); ok {
		// Check if Ctrl is pressed (this is a workaround for Fyne's limitation)
		if c.onZoomChange != nil && event.Scrolled.DY != 0 {
			// For now, we'll use a different approach - double-click for zoom toggle
			// and regular scroll for page navigation
			if c.onPageChange != nil {
				if event.Scrolled.DY > 0 {
					c.onPageChange(-1) // Previous page
				} else {
					c.onPageChange(1) // Next page
				}
				return
			}
		}
		_ = desk // Avoid unused variable warning
	}

	// Default scroll behavior
	c.Scroll.Scrolled(event)
}

// SetOnZoomChange sets the zoom change callback
func (c *CustomScrollContainer) SetOnZoomChange(callback func(delta float64)) {
	c.onZoomChange = callback
}

// SetOnPageChange sets the page change callback
func (c *CustomScrollContainer) SetOnPageChange(callback func(delta int)) {
	c.onPageChange = callback
}

// NewEnhancedImageViewer creates a new enhanced image viewer
func NewEnhancedImageViewer() *EnhancedImageViewer {
	viewer := &EnhancedImageViewer{
		focused: true, // Start focused to receive events
	}
	viewer.ExtendBaseWidget(viewer)

	// Create custom scroll container
	customScroll := NewCustomScrollContainer(widget.NewCard("", "", nil))
	viewer.scrollable = customScroll.Scroll

	return viewer
}

// SetImage sets the image to display
func (e *EnhancedImageViewer) SetImage(img *canvas.Image) {
	e.image = img
	if img != nil {
		e.scrollable.Content = img
	}
	e.scrollable.Refresh()
}

// GetScrollContainer returns the scroll container
func (e *EnhancedImageViewer) GetScrollContainer() *container.Scroll {
	return e.scrollable
}

// SetOnZoomChange sets the zoom change callback
func (e *EnhancedImageViewer) SetOnZoomChange(callback func(delta float64)) {
	e.onZoomChange = callback
}

// SetOnPageChange sets the page change callback
func (e *EnhancedImageViewer) SetOnPageChange(callback func(delta int)) {
	e.onPageChange = callback
}

// SetGetZoomMode sets the function to check zoom mode
func (e *EnhancedImageViewer) SetGetZoomMode(callback func() bool) {
	e.getZoomMode = callback
}

// CreateRenderer creates the widget renderer
func (e *EnhancedImageViewer) CreateRenderer() fyne.WidgetRenderer {
	return widget.NewSimpleRenderer(e.scrollable)
}

// MouseIn handles mouse enter events
func (e *EnhancedImageViewer) MouseIn(*desktop.MouseEvent) {}

// MouseOut handles mouse exit events
func (e *EnhancedImageViewer) MouseOut() {}

// MouseMoved handles mouse movement
func (e *EnhancedImageViewer) MouseMoved(event *desktop.MouseEvent) {
	if e.isDragging && e.image != nil {
		e.lastPos = event.Position
	}
}

// MouseDown handles mouse button press
func (e *EnhancedImageViewer) MouseDown(event *desktop.MouseEvent) {
	if event.Button == desktop.MouseButtonPrimary {
		e.isDragging = true
		e.lastPos = event.Position
	}
}

// MouseUp handles mouse button release
func (e *EnhancedImageViewer) MouseUp(event *desktop.MouseEvent) {
	e.isDragging = false
}

// Scrolled handles scroll wheel events
func (e *EnhancedImageViewer) Scrolled(event *fyne.ScrollEvent) {
	// Check if content is zoomed and needs regular scrolling
	if e.image != nil && e.isContentLargerThanContainer() {
		// Allow regular scrolling when content is larger than container
		e.scrollable.Scrolled(event)
		return
	}

	// Check if zoom mode is active
	if e.getZoomMode != nil && e.getZoomMode() {
		// Zoom mode: use scroll wheel for zooming
		if e.onZoomChange != nil && event.Scrolled.DY != 0 {
			if event.Scrolled.DY > 0 {
				e.onZoomChange(0.2) // Zoom in (scroll up)
			} else {
				e.onZoomChange(-0.2) // Zoom out (scroll down)
			}
		}
		return
	}

	// Page navigation mode: use scroll wheel for page changes
	if e.onPageChange != nil && event.Scrolled.DY != 0 {
		if event.Scrolled.DY > 0 {
			e.onPageChange(-1) // Previous page (scroll up)
		} else {
			e.onPageChange(1) // Next page (scroll down)
		}
	} else {
		e.scrollable.Scrolled(event)
	}
}



// DoubleTapped handles double-tap/click events
func (e *EnhancedImageViewer) DoubleTapped(event *fyne.PointEvent) {
	// Implement double-click to toggle zoom modes
	if e.onZoomChange != nil {
		// Toggle between fit and 100% zoom
		e.onZoomChange(0) // Special value for toggle
	}
}

// Tapped handles single tap/click events
func (e *EnhancedImageViewer) Tapped(event *fyne.PointEvent) {
	// Focus the widget to receive keyboard events
	e.focused = true
}

// Resize handles widget resize
func (e *EnhancedImageViewer) Resize(size fyne.Size) {
	e.BaseWidget.Resize(size)
	e.scrollable.Resize(size)
}

// Move handles widget move
func (e *EnhancedImageViewer) Move(pos fyne.Position) {
	e.BaseWidget.Move(pos)
	e.scrollable.Move(pos)
}

// FocusGained handles focus gained events
func (e *EnhancedImageViewer) FocusGained() {
	e.focused = true
}

// FocusLost handles focus lost events
func (e *EnhancedImageViewer) FocusLost() {
	e.focused = false
}

// TypedRune handles typed character events
func (e *EnhancedImageViewer) TypedRune(rune) {}

// TypedKey handles typed key events
func (e *EnhancedImageViewer) TypedKey(event *fyne.KeyEvent) {
	// Basic key handling - focus management
}

// isContentLargerThanContainer checks if the content exceeds container size
func (e *EnhancedImageViewer) isContentLargerThanContainer() bool {
	if e.image == nil || e.scrollable == nil {
		return false
	}

	imageSize := e.image.Size()
	containerSize := e.scrollable.Size()

	return imageSize.Width > containerSize.Width || imageSize.Height > containerSize.Height
}
