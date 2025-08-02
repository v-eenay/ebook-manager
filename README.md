# Modern EBook Reader

A clean, minimal ebook reader application built with Python and Qt, supporting PDF, EPUB, and MOBI formats with a focus on distraction-free reading.

## ✨ Features

- **Multi-format Support**: Read PDF, EPUB, and MOBI files
- **Modern Interface**: Clean, minimal design with content-first approach
- **Responsive Performance**: Fast document loading and smooth navigation
- **Zoom Controls**: Zoom in/out with mouse wheel or keyboard shortcuts
- **Keyboard Navigation**: Complete set of navigation shortcuts
- **Drag & Drop**: Simply drag files into the window to open them
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or later
- PyQt6 or PyQt5

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/v-eenay/ebook-manager.git
   cd ebook-manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Alternative Installation (using pip)

```bash
pip install -e .
ebook-reader
```

## 📖 Usage

### Opening Documents

- **File Menu**: Click "Open Document" or press `Ctrl+O`
- **Drag & Drop**: Drag PDF, EPUB, or MOBI files directly into the window
- **Welcome Screen**: Use the "Open Document" button on the welcome screen

### Navigation

- **Arrow Keys**: Navigate between pages (`←` / `→`)
- **Mouse Wheel**: Scroll through pages
- **Keyboard Shortcuts**: `Home`/`End` for first/last page
- **Page Up/Down**: Navigate pages

### Zoom Controls

- **Mouse Wheel**: Hold `Ctrl` while scrolling to zoom
- **Keyboard**: `Ctrl +/-` to zoom in/out
- **Toolbar**: Use zoom buttons in the toolbar

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open document |
| `←` / `→` | Previous/Next page |
| `Home` / `End` | First/Last page |
| `Page Up` / `Page Down` | Navigate pages |
| `Ctrl +` / `Ctrl -` | Zoom in/out |

## 🏗️ Architecture

```
ebook-manager/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── assets/                      # Application assets
│   └── icon.png                # Application icon
├── src/                         # Source code
│   ├── ui/                      # User interface components
│   │   ├── main_window.py      # Main application window
│   │   ├── document_viewer.py  # Document display widget
│   │   └── welcome_widget.py   # Welcome screen
│   ├── readers/                 # Document reading engines
│   │   ├── document_manager.py # Document loading manager
│   │   ├── base_reader.py      # Abstract base reader
│   │   ├── pdf_reader.py       # PDF support (PyMuPDF)
│   │   ├── epub_reader.py      # EPUB support (ebooklib)
│   │   └── mobi_reader.py      # MOBI support (basic)
│   └── utils/                   # Utility modules
├── LICENSE                      # MIT License
└── README.md                   # This file
```

## 🔧 Development

### Setting up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/v-eenay/ebook-manager.git
   cd ebook-manager
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

### Dependencies

- **PyQt6/PyQt5**: Cross-platform GUI framework
- **PyMuPDF**: PDF rendering and processing
- **ebooklib**: EPUB reading and processing
- **BeautifulSoup4**: HTML parsing for EPUB/MOBI
- **Pillow**: Image handling and conversion

## 📋 Supported Formats

| Format | Support Level | Features |
|--------|---------------|----------|
| **PDF** | Full | High-quality rendering, zoom, navigation |
| **EPUB** | Good | Text extraction, chapter navigation |
| **MOBI** | Basic | Text extraction, basic navigation |

## 🎯 Design Philosophy

This application follows modern UI/UX principles:

- **Minimal Design**: Clean, distraction-free interface
- **Content First**: Document content is the primary focus
- **Responsive**: Fast, snappy interactions
- **Accessible**: High contrast, readable typography
- **Professional**: Suitable for productivity use

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyQt](https://www.riverbankcomputing.com/software/pyqt/) for the excellent GUI framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF rendering capabilities
- [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB support
- The open-source community for various libraries and tools
