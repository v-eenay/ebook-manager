package modernui

import (
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/widget"
	"fyne.io/fyne/v2/canvas"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/driver/desktop"
)

// EnhancedImageViewer provides advanced mouse interaction for document viewing
type EnhancedImageViewer struct {
	widget.BaseWidget
	
	image        *canvas.Image
	scrollable   *container.Scroll
	onZoomChange func(delta float64)
	onPageChange func(delta int)
	
	// Mouse state
	isDragging   bool
	lastPos      fyne.Position
}

// NewEnhancedImageViewer creates a new enhanced image viewer
func NewEnhancedImageViewer() *EnhancedImageViewer {
	viewer := &EnhancedImageViewer{}
	viewer.ExtendBaseWidget(viewer)
	
	// Create scroll container
	viewer.scrollable = container.NewScroll(widget.NewCard("", "", nil))
	
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

// CreateRenderer creates the widget renderer
func (e *EnhancedImageViewer) CreateRenderer() fyne.WidgetRenderer {
	return widget.NewSimpleRenderer(e.scrollable)
}

// MouseIn handles mouse enter events
func (e *EnhancedImageViewer) MouseIn(*desktop.MouseEvent) {
	// Could be used for hover effects
}

// MouseOut handles mouse exit events
func (e *EnhancedImageViewer) MouseOut() {
	// Could be used for hover effects
}

// MouseMoved handles mouse movement
func (e *EnhancedImageViewer) MouseMoved(event *desktop.MouseEvent) {
	if e.isDragging && e.image != nil {
		// Calculate drag delta (for future implementation)
		_ = event.Position.X - e.lastPos.X // deltaX
		_ = event.Position.Y - e.lastPos.Y // deltaY

		// Update scroll position (this would need custom implementation)
		// For now, Fyne's scroll container handles this automatically

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
	// For now, use simple scroll behavior
	// Advanced modifier key detection would require platform-specific implementation

	// Regular vertical scrolling
	// For documents, we might want page-based scrolling
	if e.onPageChange != nil && event.Scrolled.DY != 0 {
		if event.Scrolled.DY > 0 {
			e.onPageChange(-1) // Previous page
		} else {
			e.onPageChange(1) // Next page
		}
	} else {
		// Default scroll behavior
		e.scrollable.Scrolled(event)
	}
}

// Tapped handles tap/click events
func (e *EnhancedImageViewer) Tapped(event *fyne.PointEvent) {
	// Could be used for click-to-zoom or other interactions
}

// DoubleTapped handles double-tap/click events
func (e *EnhancedImageViewer) DoubleTapped(event *fyne.PointEvent) {
	// Could implement double-click to fit/zoom
	if e.onZoomChange != nil {
		// Toggle between fit and 100% zoom
		e.onZoomChange(0) // Special value for toggle
	}
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
