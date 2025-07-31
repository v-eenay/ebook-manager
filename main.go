package main

import (
	"os"
	"path/filepath"

	"ebookreader/ui"
)

func main() {
	// Create and run the application
	app := ui.NewApplication()

	// Check for command line arguments (PDF file)
	if len(os.Args) > 1 {
		pdfFile := os.Args[1]
		if filepath.Ext(pdfFile) == ".pdf" {
			// TODO: Load PDF from command line argument
			// This would require exposing a LoadPDF method in the Application
		}
	}

	// Run the application
	app.Run()
}
