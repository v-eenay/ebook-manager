package qtui

import (
	"bytes"
	"image"
	"image/png"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/gui"
)

// imageToQPixmap converts an image.Image to QPixmap
func imageToQPixmap(img image.Image) *gui.QPixmap {
	// Convert image to PNG bytes
	var buf bytes.Buffer
	err := png.Encode(&buf, img)
	if err != nil {
		return gui.NewQPixmap()
	}

	// Create QPixmap from bytes
	pixmap := gui.NewQPixmap()
	pixmap.LoadFromData(buf.Bytes(), uint(len(buf.Bytes())), "PNG", core.Qt__AutoColor)
	
	return pixmap
}
