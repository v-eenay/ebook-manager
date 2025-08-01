# Modern EBook Reader

A modern, cross-platform desktop ebook reader built with Go and Fyne, supporting multiple document formats with enhanced UI, zoom controls, keyboard shortcuts, and comprehensive help system.

## Features

### Supported Formats
- **PDF**: High-quality rendering with MuPDF (go-fitz)
- **EPUB**: Full support with custom parser
- **MOBI**: Basic text extraction and reading

### Modern Interface
- Clean, tabbed interface built with Fyne
- Professional application icon integration
- Renamed "Reader" tab for multi-format support
- Enhanced visual hierarchy with modern styling
- Responsive design that adapts to window size
- Modern navigation controls with icons
- Improved toolbar with organized sections

### Enhanced Navigation & Controls
- Page-by-page navigation (PDF)
- Scroll-based reading (EPUB/MOBI)
- Mouse wheel scrolling support
- Jump to specific pages
- First/Previous/Next/Last page controls
- Comprehensive keyboard shortcuts (F1 for help)

### Zoom & Viewing Options
- Zoom in/out controls with visual feedback
- Fit to Page and Fit to Width options
- Real-time zoom level display
- Pan/drag functionality for zoomed documents
- Multiple viewing modes for optimal reading

### User Experience
- Drag and drop file support
- Real-time page indicators
- Document information display
- Comprehensive help system (F1 key)
- Quick help for essential shortcuts
- Cross-platform compatibility (Windows, macOS, Linux)
- Fully offline operation

## Building

### Prerequisites
- Go 1.19 or later
- C compiler (for go-fitz)
  - Windows: MinGW-w64 or Visual Studio
  - macOS: Xcode command line tools
  - Linux: GCC

### Build Instructions
```bash
# Install Fyne tools for icon integration
go install fyne.io/tools/cmd/fyne@latest

# Download dependencies
go mod download

# Standard build with embedded icon
go build -o ebookreader-modern.exe

# Optimized build (recommended)
go build -ldflags="-s -w" -o ebookreader-modern.exe .

# Use build scripts for enhanced features
.\build.bat     # Windows batch script
.\build.ps1     # PowerShell script (recommended)
```

### Icon Integration
The application includes professional icon integration:
- Embedded icon resources using Fyne's resource system
- System-level icon display (taskbar, title bar)
- UI integration in welcome screen and help dialogs
- Cross-platform compatibility (Windows, macOS, Linux)

## Usage

### Running the Application
```bash
./ebookreader-modern.exe
```

### Opening Documents
1. Click "Open Document" button in the toolbar
2. Drag and drop files onto the application window
3. Supported file extensions: `.pdf`, `.epub`, `.mobi`

### Navigation & Controls
- Use arrow buttons for page navigation
- Enter page numbers directly in the page field
- Switch between Reader and Text View tabs
- Use mouse wheel for scrolling and page navigation
- Keyboard shortcuts for all major functions

### Keyboard Shortcuts
- **F1** - Show complete help guide
- **Ctrl+O** - Open document
- **← →** - Previous/Next page
- **Page Up/Down** - Navigate pages
- **Home/End** - First/Last page
- **Ctrl + +/-** - Zoom in/out
- **Ctrl+0** - Reset zoom to 100%
- **Ctrl+1** - Fit to page
- **Ctrl+2** - Fit to width

### Zoom Controls
- Use toolbar zoom buttons
- Ctrl+mouse wheel for zoom (where supported)
- Fit to Page/Width buttons for optimal viewing
- Real-time zoom percentage display

## Project Structure

```
ebook-manager/
├── main.go                      # Application entry point
├── assets/                      # Application assets
│   └── icon.png                # Application icon
├── modernui/                    # Modern Fyne-based UI
│   ├── app.go                  # Main application logic
│   ├── enhanced_viewer.go      # Enhanced mouse interaction widget
│   ├── resource.go             # Embedded icon resource (auto-generated)
│   └── app_test.go             # Unit tests for UI components
├── reader/                      # Document reading engine
│   ├── document.go             # Document interface and manager
│   ├── pdf.go                  # PDF support (go-fitz)
│   ├── epub.go                 # EPUB support (custom parser)
│   └── mobi.go                 # MOBI support (basic)
├── build.ps1                   # PowerShell build script
├── build.bat                   # Batch build script
├── go.mod                      # Go module definition
├── go.sum                      # Dependency checksums
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## Architecture

### Document Interface
The application uses a flexible document interface that allows easy extension to support additional formats:

```go
type Document interface {
    GetPageCount() int
    GetPage(pageNum int) (*Page, error)
    GetMetadata() *Metadata
    Close() error
}
```

### Format Support
- **PDF**: Uses MuPDF via go-fitz for high-quality rendering
- **EPUB**: Custom ZIP-based parser with HTML-to-text conversion
- **MOBI**: Simplified text extraction with basic pagination

### UI Framework
Built with Fyne v2.6.2 for:
- Native look and feel across platforms
- Hardware-accelerated rendering
- Touch and high-DPI support
- Comprehensive widget set

## Dependencies

- `fyne.io/fyne/v2` - Modern GUI framework
- `github.com/gen2brain/go-fitz` - PDF rendering (MuPDF bindings)
- `archive/zip` - EPUB file handling
- `encoding/xml` - EPUB metadata parsing
- Standard Go libraries for file handling and UI

## Testing

The project includes comprehensive unit tests and benchmarks:

```bash
# Run all tests
go test ./modernui -v

# Run benchmarks
go test -bench=. ./modernui

# Build and test
go build -o ebookreader-modern.exe .
```

### Test Coverage
- Application structure validation
- Zoom functionality testing
- Fit mode operations
- UI component initialization
- Keyboard shortcuts mapping
- Enhanced viewer functionality
- Performance benchmarks

## Future Enhancements

- Advanced zoom with Ctrl+mouse wheel (platform-specific)
- Custom themes and dark mode support
- Bookmarks and annotations system
- Full-text search across documents
- Reading progress tracking
- Recent files quick access
- Cloud integration and sync
- Additional format support (TXT, RTF, etc.)
- Reading statistics and analytics
- Full-screen reading mode

## Author

**Binay Koirala**

- 🌐 **LinkedIn**: [linkedin.com/in/veenay](https://linkedin.com/in/veenay)
- 🐙 **GitHub**: [github.com/v-eenay](https://github.com/v-eenay)
- 📧 **Email**: [koiralavinay@gmail.com](mailto:koiralavinay@gmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright © 2025 Binay Koirala. All rights reserved.

## Acknowledgments

- [Fyne](https://fyne.io/) - Modern GUI framework for Go
- [go-fitz](https://github.com/gen2brain/go-fitz) - MuPDF bindings for PDF rendering
- [MuPDF](https://mupdf.com/) - Lightweight PDF and XPS viewer
- Go community for excellent libraries and tools

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**
