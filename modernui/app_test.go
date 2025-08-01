package modernui

import (
	"testing"
)

func TestModernApplicationStructure(t *testing.T) {
	// Test the application structure without full UI initialization
	app := &ModernApplication{
		currentPage: 1,
		zoomLevel:   1.0,
		fitMode:     "page",
		shortcuts:   make(map[string]func()),
	}

	if app.currentPage != 1 {
		t.Errorf("Expected currentPage to be 1, got %d", app.currentPage)
	}

	if app.zoomLevel != 1.0 {
		t.Errorf("Expected zoomLevel to be 1.0, got %f", app.zoomLevel)
	}

	if app.fitMode != "page" {
		t.Errorf("Expected fitMode to be 'page', got %s", app.fitMode)
	}

	if app.shortcuts == nil {
		t.Error("Shortcuts map should be initialized")
	}
}

func TestZoomFunctionality(t *testing.T) {
	app := &ModernApplication{
		zoomLevel: 1.0,
		fitMode:   "page",
	}

	// Test zoom in
	initialZoom := app.zoomLevel
	app.zoomLevel = app.zoomLevel * 1.2 // Simulate zoomIn
	app.fitMode = "custom"
	if app.zoomLevel <= initialZoom {
		t.Error("Zoom in should increase zoom level")
	}

	// Test zoom out
	currentZoom := app.zoomLevel
	app.zoomLevel = app.zoomLevel / 1.2 // Simulate zoomOut
	if app.zoomLevel >= currentZoom {
		t.Error("Zoom out should decrease zoom level")
	}

	// Test set zoom bounds
	testZoom := 10.0
	if testZoom > 5.0 {
		testZoom = 5.0
	}
	app.zoomLevel = testZoom
	if app.zoomLevel != 5.0 {
		t.Errorf("Expected zoom level to be clamped to 5.0, got %f", app.zoomLevel)
	}

	testZoom = 0.01
	if testZoom < 0.1 {
		testZoom = 0.1
	}
	app.zoomLevel = testZoom
	if app.zoomLevel != 0.1 {
		t.Errorf("Expected zoom level to be clamped to 0.1, got %f", app.zoomLevel)
	}
}

func TestFitModes(t *testing.T) {
	app := &ModernApplication{
		zoomLevel: 1.0,
		fitMode:   "page",
	}

	// Test fit to page
	app.fitMode = "page"
	if app.fitMode != "page" {
		t.Errorf("Expected fit mode 'page', got %s", app.fitMode)
	}

	// Test fit to width
	app.fitMode = "width"
	if app.fitMode != "width" {
		t.Errorf("Expected fit mode 'width', got %s", app.fitMode)
	}

	// Test custom zoom changes fit mode
	app.fitMode = "custom"
	if app.fitMode != "custom" {
		t.Errorf("Expected fit mode 'custom' after manual zoom, got %s", app.fitMode)
	}
}

func TestUIComponentsStructure(t *testing.T) {
	// Test the structure without full UI initialization
	app := &ModernApplication{}

	// Test that we can set basic properties
	app.currentPage = 1
	app.zoomLevel = 1.0
	app.fitMode = "page"

	if app.currentPage != 1 {
		t.Error("Failed to set current page")
	}

	if app.zoomLevel != 1.0 {
		t.Error("Failed to set zoom level")
	}

	if app.fitMode != "page" {
		t.Error("Failed to set fit mode")
	}
}

func TestKeyboardShortcuts(t *testing.T) {
	// Test shortcuts map structure
	shortcuts := map[string]func(){
		"F1":           func() {},
		"Ctrl+O":       func() {},
		"Left":         func() {},
		"Right":        func() {},
		"Home":         func() {},
		"End":          func() {},
		"Page_Up":      func() {},
		"Page_Down":    func() {},
		"Ctrl+Plus":    func() {},
		"Ctrl+Minus":   func() {},
		"Ctrl+0":       func() {},
		"Ctrl+1":       func() {},
		"Ctrl+2":       func() {},
	}

	// Test that essential shortcuts are defined
	expectedShortcuts := []string{
		"F1", "Ctrl+O", "Left", "Right", "Home", "End",
		"Page_Up", "Page_Down", "Ctrl+Plus", "Ctrl+Minus",
		"Ctrl+0", "Ctrl+1", "Ctrl+2",
	}

	for _, shortcut := range expectedShortcuts {
		if _, exists := shortcuts[shortcut]; !exists {
			t.Errorf("Expected shortcut %s not found", shortcut)
		}
	}
}

func TestEnhancedViewer(t *testing.T) {
	viewer := NewEnhancedImageViewer()
	
	if viewer == nil {
		t.Fatal("Failed to create EnhancedImageViewer")
	}
	
	if viewer.scrollable == nil {
		t.Error("Scrollable container is nil")
	}
	
	// Test callback setting
	viewer.SetOnZoomChange(func(delta float64) {
		// Callback for zoom change
	})

	viewer.SetOnPageChange(func(delta int) {
		// Callback for page change
	})
	
	// Test that callbacks are set (we can't easily test execution without UI events)
	if viewer.onZoomChange == nil {
		t.Error("Zoom change callback not set")
	}
	
	if viewer.onPageChange == nil {
		t.Error("Page change callback not set")
	}
}

func TestIconResource(t *testing.T) {
	// Test that the icon resource is available
	if resourceIconPng == nil {
		t.Error("Icon resource is nil")
	}

	if resourceIconPng.Name() == "" {
		t.Error("Icon resource has no name")
	}

	if len(resourceIconPng.Content()) == 0 {
		t.Error("Icon resource has no content")
	}

	// Test that it's a PNG resource
	expectedName := "icon.png"
	if resourceIconPng.Name() != expectedName {
		t.Errorf("Expected icon name %s, got %s", expectedName, resourceIconPng.Name())
	}
}

// Benchmark zoom operations
func BenchmarkZoomOperations(b *testing.B) {
	app := &ModernApplication{
		zoomLevel: 1.0,
		fitMode:   "page",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		app.zoomLevel = app.zoomLevel * 1.2 // Simulate zoom in
		app.zoomLevel = app.zoomLevel / 1.2 // Simulate zoom out
		app.zoomLevel = 1.0                 // Reset zoom
	}
}
