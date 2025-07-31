# Modern EBook Reader

A modern, cross-platform desktop ebook reader built with Go and Fyne, supporting multiple document formats.

## Features

### Supported Formats
- **PDF**: High-quality rendering with MuPDF (go-fitz)
- **EPUB**: Full support with custom parser
- **MOBI**: Basic text extraction and reading

### Modern Interface
- Clean, tabbed interface built with Fyne
- Dual view modes: PDF view and text view
- Responsive design that adapts to window size
- Modern navigation controls with icons

### Navigation
- Page-by-page navigation (PDF)
- Scroll-based reading (EPUB/MOBI)
- Jump to specific pages
- First/Previous/Next/Last page controls
- Keyboard shortcuts

### User Experience
- Drag and drop file support
- Real-time page indicators
- Document information display
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
go mod download
go build -o ebookreader-modern.exe
```

## Usage

### Running the Application
```bash
./ebookreader-modern.exe
```

### Opening Documents
1. Click "Open" button in the toolbar
2. Drag and drop files onto the application window
3. Supported file extensions: `.pdf`, `.epub`, `.mobi`

### Navigation
- Use arrow buttons for page navigation
- Enter page numbers directly in the page field
- Switch between PDF and Text views using tabs

## Project Structure

```
ebook-manager/
├── main.go              # Application entry point
├── modernui/            # Modern Fyne-based UI
│   └── app.go          # Main application logic
├── reader/              # Document reading engine
│   ├── document.go     # Document interface and manager
│   ├── pdf.go          # PDF support (go-fitz)
│   ├── epub.go         # EPUB support (custom parser)
│   └── mobi.go         # MOBI support (basic)
├── go.mod              # Go module definition
├── go.sum              # Dependency checksums
└── README.md           # This file
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

## Future Enhancements

- Bookmarks and annotations
- Full-text search across documents
- Reading progress tracking
- Theme customization
- Additional format support (TXT, RTF, etc.)
- Reading statistics and analytics

## License

This project is open source and available under the MIT License.
- Drag & drop support
