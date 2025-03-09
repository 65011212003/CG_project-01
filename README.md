# 2D Drawing Application

A simple yet powerful drawing application built with Python and Tkinter.

## Features

- Draw various shapes: lines, rectangles, ovals, circles, polygons
- Add text to your drawings
- Choose outline and fill colors
- Adjust line width
- Undo/Redo functionality
- Save and open drawings
- Select and move shapes
- Delete selected shapes

## How to Use

1. Launch the application by running the executable file
2. Select a shape from the toolbar
3. Click and drag on the canvas to draw
4. Use the color buttons to change outline and fill colors
5. Adjust line width using the spinbox
6. Save your work using File > Save
7. Open previous drawings using File > Open

## Keyboard Shortcuts

- Ctrl+Z: Undo
- Ctrl+Y: Redo
- Delete: Delete selected shape

## Building from Source

If you want to build the application from source:

1. Install Python 3.x
2. Install required packages: `pip install pillow pyinstaller`
3. Run `pyinstaller drawing_app.spec`
4. The executable will be created in the `dist` folder

## License

This project is open source and available under the MIT License. 