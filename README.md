# eBook Manager

A desktop eBook manager built with Electron, Vite, and React.

## Features

- 📚 Modern desktop application built with Electron
- ⚡ Fast development with Vite and Hot Module Replacement (HMR)
- ⚛️ React 18 with TypeScript
- 🎨 Clean and responsive UI
- 🔧 Development and production build support

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ebook-manager
```

2. Install dependencies:
```bash
npm install
```

### Development

To start the application in development mode with hot reloading:

```bash
npm run electron:dev
```

This command will:
- Start the Vite development server
- Launch the Electron application
- Enable hot module replacement for instant updates

### Building

To build the application for production:

```bash
npm run dist
```

This will create platform-specific installers in the `release` folder.

### Available Scripts

- `npm run dev` - Start Vite development server
- `npm run build` - Build for production
- `npm run electron:dev` - Start Electron with development server
- `npm run electron:preview` - Start Electron with production build
- `npm run dist` - Build and package the application

## Project Structure

```
ebook-manager/
├── electron/          # Electron main process files
│   ├── main.ts        # Main process entry point
│   └── preload.ts     # Preload script for secure IPC
├── src/               # React application source
│   ├── App.tsx        # Main React component
│   ├── App.css        # Application styles
│   ├── main.tsx       # React entry point
│   └── index.css      # Global styles
├── public/            # Static assets
├── dist/              # Built React application
├── dist-electron/     # Built Electron files
└── release/           # Packaged applications
```

## Architecture

- **Main Process (Electron)**: Handles window management, system integration, and security
- **Renderer Process (React)**: The user interface built with React and Vite
- **Preload Script**: Secure bridge between main and renderer processes

## Security

This application follows Electron security best practices:
- Context isolation enabled
- Node integration disabled in renderer
- Secure IPC communication through preload scripts

## Future Features

- 📚 Import and organize eBooks (EPUB, PDF, etc.)
- 🔍 Advanced search and filtering
- 📖 Built-in eBook reader
- 🏷️ Tagging and categorization
- 📊 Reading progress tracking
- 🌙 Dark/light theme support
- ☁️ Cloud synchronization

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
