import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog, simpledialog
import math
import json
import os
from PIL import Image, ImageTk

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2D Drawing Application")
        
        # Apply theme
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')  # Using a more modern built-in theme
        except tk.TclError:
            pass  # Fallback if theme not available
        
        # Configure style
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Tool.TButton', padding=5)
        self.style.configure('Selected.TButton', background='#c0c0ff', relief='sunken')

        # Variables
        self.current_shape = "line"
        self.current_color = "#000000"  # Black
        self.fill_color = "#ffffff"     # White
        self.start_x = None
        self.start_y = None
        self.drawn_items = []
        self.line_width = 2
        self.undo_stack = []
        self.redo_stack = []
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create canvas with border
        self.canvas_frame = ttk.Frame(self.main_frame, borderwidth=2, relief="groove")
        self.canvas_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=600, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Create menu bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.clear_canvas, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Save", command=self.save_drawing, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Open", command=self.open_drawing, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit, accelerator="Alt+F4")
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        
        # Create toolbar with sections
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Separator function
        def add_separator():
            separator = ttk.Separator(self.toolbar, orient='vertical')
            separator.pack(side=tk.LEFT, padx=10, pady=5, fill='y')
        
        # Tools section
        self.tools_frame = ttk.LabelFrame(self.toolbar, text="Tools")
        self.tools_frame.pack(side=tk.LEFT, padx=5, pady=5, fill='y')
        
        # Button dict to keep track of tool buttons
        self.tool_buttons = {}
        
        # Shape buttons
        self.tool_buttons["line"] = ttk.Button(self.tools_frame, text="Line", width=10, 
                                            command=lambda: self.set_shape("line"), style='Tool.TButton')
        self.tool_buttons["line"].pack(side=tk.LEFT, padx=2, pady=2)
        
        self.tool_buttons["rectangle"] = ttk.Button(self.tools_frame, text="Rectangle", width=10,
                                                 command=lambda: self.set_shape("rectangle"), style='Tool.TButton')
        self.tool_buttons["rectangle"].pack(side=tk.LEFT, padx=2, pady=2)
        
        self.tool_buttons["oval"] = ttk.Button(self.tools_frame, text="Oval", width=10,
                                            command=lambda: self.set_shape("oval"), style='Tool.TButton')
        self.tool_buttons["oval"].pack(side=tk.LEFT, padx=2, pady=2)
        
        self.tool_buttons["circle"] = ttk.Button(self.tools_frame, text="Circle", width=10,
                                              command=lambda: self.set_shape("circle"), style='Tool.TButton')
        self.tool_buttons["circle"].pack(side=tk.LEFT, padx=2, pady=2)
        
        self.tool_buttons["polygon"] = ttk.Button(self.tools_frame, text="Polygon", width=10,
                                               command=lambda: self.set_shape("polygon"), style='Tool.TButton')
        self.tool_buttons["polygon"].pack(side=tk.LEFT, padx=2, pady=2)
        
        self.tool_buttons["text"] = ttk.Button(self.tools_frame, text="Text", width=10,
                                            command=lambda: self.set_shape("text"), style='Tool.TButton')
        self.tool_buttons["text"].pack(side=tk.LEFT, padx=2, pady=2)
        
        # Highlight the default tool
        self.tool_buttons["line"].state(['pressed'])
        
        add_separator()
        
        # Color section
        self.color_frame = ttk.LabelFrame(self.toolbar, text="Colors")
        self.color_frame.pack(side=tk.LEFT, padx=5, pady=5, fill='y')
        
        # Create color preview frames
        self.outline_preview = tk.Frame(self.color_frame, width=20, height=20, bg=self.current_color, bd=1, relief='sunken')
        self.outline_preview.pack(side=tk.LEFT, padx=(5, 2), pady=5)
        
        self.color_btn = ttk.Button(self.color_frame, text="Outline", command=self.choose_color)
        self.color_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        self.fill_preview = tk.Frame(self.color_frame, width=20, height=20, bg=self.fill_color, bd=1, relief='sunken')
        self.fill_preview.pack(side=tk.LEFT, padx=(10, 2), pady=5)
        
        self.fill_btn = ttk.Button(self.color_frame, text="Fill", command=self.choose_fill_color)
        self.fill_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        add_separator()
        
        # Line width section
        self.width_frame = ttk.LabelFrame(self.toolbar, text="Line Width")
        self.width_frame.pack(side=tk.LEFT, padx=5, pady=5, fill='y')
        
        self.width_var = tk.StringVar(value="2")
        self.width_spinbox = ttk.Spinbox(self.width_frame, from_=1, to=10, width=3, textvariable=self.width_var, 
                                        command=self.update_line_width)
        self.width_spinbox.pack(side=tk.LEFT, padx=5, pady=5)
        
        add_separator()
        
        # Actions section
        self.actions_frame = ttk.LabelFrame(self.toolbar, text="Actions")
        self.actions_frame.pack(side=tk.LEFT, padx=5, pady=5, fill='y')
        
        # Undo/Redo buttons
        self.undo_btn = ttk.Button(self.actions_frame, text="Undo", command=self.undo)
        self.undo_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        self.redo_btn = ttk.Button(self.actions_frame, text="Redo", command=self.redo)
        self.redo_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Clear and delete buttons
        self.clear_btn = ttk.Button(self.actions_frame, text="Clear All", command=self.clear_canvas)
        self.clear_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        self.delete_btn = ttk.Button(self.actions_frame, text="Delete Item", command=self.delete_selected)
        self.delete_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-1>", self.on_double_click)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<Delete>", lambda event: self.delete_selected())
        self.root.bind("<Control-n>", lambda event: self.clear_canvas())
        self.root.bind("<Control-s>", lambda event: self.save_drawing())
        self.root.bind("<Control-o>", lambda event: self.open_drawing())
        
        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Coordinates display
        self.coords_label = ttk.Label(self.status_frame, text="", relief=tk.SUNKEN, width=15)
        self.coords_label.pack(side=tk.RIGHT)
        
        # Update coordinates on mouse movement
        self.canvas.bind("<Motion>", self.update_coords)
        
        # Temporary shape for preview
        self.temp_shape = None
        self.selected_item = None
        self.polygon_points = []
        
        # Update initial UI state
        self.update_tool_buttons()
    
    def update_coords(self, event):
        """Update coordinates display in status bar"""
        self.coords_label.config(text=f"X: {event.x}, Y: {event.y}")
        
    def update_tool_buttons(self):
        """Update tool button styling based on selected shape"""
        for shape, button in self.tool_buttons.items():
            if shape == self.current_shape:
                button.state(['pressed'])
            else:
                button.state(['!pressed'])
    
    def set_shape(self, shape):
        self.current_shape = shape
        self.status_bar.config(text=f"Selected: {shape.capitalize()}")
        
        # Update button styling
        self.update_tool_buttons()
        
        # Reset polygon points if changing from polygon
        if shape != "polygon":
            self.polygon_points = []
    
    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.outline_preview.config(bg=self.current_color)
    
    def choose_fill_color(self):
        color = colorchooser.askcolor(initialcolor=self.fill_color if self.fill_color else "#ffffff")
        if color[1]:
            self.fill_color = color[1]
            self.fill_preview.config(bg=self.fill_color)
    
    def update_line_width(self):
        try:
            self.line_width = int(self.width_var.get())
        except ValueError:
            self.line_width = 2
            self.width_var.set("2")
    
    def clear_canvas(self):
        if self.drawn_items and messagebox.askyesno("Confirm", "Are you sure you want to clear the canvas?"):
            self.save_state()
            self.canvas.delete("all")
            self.drawn_items = []
            self.polygon_points = []
    
    def delete_selected(self):
        if self.selected_item:
            self.save_state()
            self.canvas.delete(self.selected_item)
            if self.selected_item in self.drawn_items:
                self.drawn_items.remove(self.selected_item)
            self.selected_item = None
    
    def save_state(self):
        # Save current state for undo
        state = []
        for item_id in self.drawn_items:
            item_type = self.canvas.type(item_id)
            coords = self.canvas.coords(item_id)
            options = {}
            
            if item_type in ["line", "oval", "rectangle", "polygon", "text"]:
                options["fill"] = self.canvas.itemcget(item_id, "fill")
                options["width"] = self.canvas.itemcget(item_id, "width")
                
                if item_type != "line":
                    options["outline"] = self.canvas.itemcget(item_id, "outline")
                
                if item_type == "text":
                    options["text"] = self.canvas.itemcget(item_id, "text")
                    options["font"] = self.canvas.itemcget(item_id, "font")
            
            state.append((item_type, coords, options))
        
        self.undo_stack.append(state)
        self.redo_stack = []  # Clear redo stack when a new action is performed
    
    def undo(self):
        if not self.undo_stack:
            return
        
        # Save current state for redo
        current_state = []
        for item_id in self.drawn_items:
            item_type = self.canvas.type(item_id)
            coords = self.canvas.coords(item_id)
            options = {}
            
            if item_type in ["line", "oval", "rectangle", "polygon", "text"]:
                options["fill"] = self.canvas.itemcget(item_id, "fill")
                options["width"] = self.canvas.itemcget(item_id, "width")
                
                if item_type != "line":
                    options["outline"] = self.canvas.itemcget(item_id, "outline")
                
                if item_type == "text":
                    options["text"] = self.canvas.itemcget(item_id, "text")
                    options["font"] = self.canvas.itemcget(item_id, "font")
            
            current_state.append((item_type, coords, options))
        
        self.redo_stack.append(current_state)
        
        # Restore previous state
        previous_state = self.undo_stack.pop()
        self.canvas.delete("all")
        self.drawn_items = []
        
        for item_type, coords, options in previous_state:
            if item_type == "line":
                item = self.canvas.create_line(coords, fill=options["fill"], width=options["width"])
            elif item_type == "rectangle":
                item = self.canvas.create_rectangle(coords, outline=options["outline"], 
                                                  fill=options["fill"], width=options["width"])
            elif item_type == "oval":
                item = self.canvas.create_oval(coords, outline=options["outline"], 
                                             fill=options["fill"], width=options["width"])
            elif item_type == "polygon":
                item = self.canvas.create_polygon(coords, outline=options["outline"], 
                                                fill=options["fill"], width=options["width"])
            elif item_type == "text":
                item = self.canvas.create_text(coords, text=options["text"], fill=options["fill"], 
                                             font=options["font"])
            
            self.drawn_items.append(item)
    
    def redo(self):
        if not self.redo_stack:
            return
        
        # Save current state for undo
        current_state = []
        for item_id in self.drawn_items:
            item_type = self.canvas.type(item_id)
            coords = self.canvas.coords(item_id)
            options = {}
            
            if item_type in ["line", "oval", "rectangle", "polygon", "text"]:
                options["fill"] = self.canvas.itemcget(item_id, "fill")
                options["width"] = self.canvas.itemcget(item_id, "width")
                
                if item_type != "line":
                    options["outline"] = self.canvas.itemcget(item_id, "outline")
                
                if item_type == "text":
                    options["text"] = self.canvas.itemcget(item_id, "text")
                    options["font"] = self.canvas.itemcget(item_id, "font")
            
            current_state.append((item_type, coords, options))
        
        self.undo_stack.append(current_state)
        
        # Restore next state
        next_state = self.redo_stack.pop()
        self.canvas.delete("all")
        self.drawn_items = []
        
        for item_type, coords, options in next_state:
            if item_type == "line":
                item = self.canvas.create_line(coords, fill=options["fill"], width=options["width"])
            elif item_type == "rectangle":
                item = self.canvas.create_rectangle(coords, outline=options["outline"], 
                                                  fill=options["fill"], width=options["width"])
            elif item_type == "oval":
                item = self.canvas.create_oval(coords, outline=options["outline"], 
                                             fill=options["fill"], width=options["width"])
            elif item_type == "polygon":
                item = self.canvas.create_polygon(coords, outline=options["outline"], 
                                                fill=options["fill"], width=options["width"])
            elif item_type == "text":
                item = self.canvas.create_text(coords, text=options["text"], fill=options["fill"], 
                                             font=options["font"])
            
            self.drawn_items.append(item)
    
    def save_drawing(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        
        drawing_data = []
        for item_id in self.drawn_items:
            item_type = self.canvas.type(item_id)
            coords = self.canvas.coords(item_id)
            options = {}
            
            if item_type in ["line", "oval", "rectangle", "polygon", "text"]:
                options["fill"] = self.canvas.itemcget(item_id, "fill")
                options["width"] = self.canvas.itemcget(item_id, "width")
                
                if item_type != "line":
                    options["outline"] = self.canvas.itemcget(item_id, "outline")
                
                if item_type == "text":
                    options["text"] = self.canvas.itemcget(item_id, "text")
                    options["font"] = self.canvas.itemcget(item_id, "font")
            
            drawing_data.append({"type": item_type, "coords": coords, "options": options})
        
        with open(file_path, 'w') as f:
            json.dump(drawing_data, f)
        
        messagebox.showinfo("Success", f"Drawing saved to {file_path}")
    
    def open_drawing(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                drawing_data = json.load(f)
            
            self.save_state()  # Save current state for undo
            self.canvas.delete("all")
            self.drawn_items = []
            
            for item_data in drawing_data:
                item_type = item_data["type"]
                coords = item_data["coords"]
                options = item_data["options"]
                
                if item_type == "line":
                    item = self.canvas.create_line(coords, fill=options["fill"], width=options["width"])
                elif item_type == "rectangle":
                    item = self.canvas.create_rectangle(coords, outline=options["outline"], 
                                                      fill=options["fill"], width=options["width"])
                elif item_type == "oval":
                    item = self.canvas.create_oval(coords, outline=options["outline"], 
                                                 fill=options["fill"], width=options["width"])
                elif item_type == "polygon":
                    item = self.canvas.create_polygon(coords, outline=options["outline"], 
                                                    fill=options["fill"], width=options["width"])
                elif item_type == "text":
                    item = self.canvas.create_text(coords, text=options["text"], fill=options["fill"], 
                                                 font=options["font"])
                
                self.drawn_items.append(item)
            
            messagebox.showinfo("Success", f"Drawing loaded from {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load drawing: {str(e)}")
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        # Check if clicking on an existing item
        clicked_items = self.canvas.find_withtag("current")
        if clicked_items and self.current_shape not in ["polygon", "text"]:
            self.selected_item = clicked_items[0]
            # Highlight the selected item
            self.canvas.itemconfig(self.selected_item, width=self.line_width+2)
        else:
            # Deselect previously selected item
            if self.selected_item:
                self.canvas.itemconfig(self.selected_item, width=self.line_width)
                self.selected_item = None
            
            # For polygon, add point
            if self.current_shape == "polygon":
                self.polygon_points.extend([event.x, event.y])
                # Draw a small circle to mark the point
                self.canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, 
                                      fill=self.current_color, outline="")
    
    def on_double_click(self, event):
        if self.current_shape == "polygon" and len(self.polygon_points) >= 6:  # At least 3 points (6 coordinates)
            self.save_state()
            item = self.canvas.create_polygon(self.polygon_points, outline=self.current_color, 
                                            fill=self.fill_color, width=self.line_width)
            self.drawn_items.append(item)
            self.polygon_points = []  # Reset for next polygon
        elif self.current_shape == "text":
            text = simpledialog.askstring("Input", "Enter text:")
            if text:
                self.save_state()
                item = self.canvas.create_text(event.x, event.y, text=text, fill=self.current_color, 
                                             font=("Arial", 12))
                self.drawn_items.append(item)
    
    def on_drag(self, event):
        if self.start_x is None or self.start_y is None:
            return
        
        # If an item is selected, move it
        if self.selected_item and self.current_shape not in ["polygon", "text"]:
            # Calculate movement
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.canvas.move(self.selected_item, dx, dy)
            self.start_x = event.x
            self.start_y = event.y
            return
        
        # Skip preview for polygon and text
        if self.current_shape in ["polygon", "text"]:
            return
        
        # Delete previous temporary shape
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
        
        # Draw temporary shape based on current selection
        if self.current_shape == "line":
            self.temp_shape = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y, 
                fill=self.current_color, width=self.line_width
            )
        elif self.current_shape == "rectangle":
            self.temp_shape = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y, 
                outline=self.current_color, fill=self.fill_color, width=self.line_width
            )
        elif self.current_shape == "oval":
            self.temp_shape = self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y, 
                outline=self.current_color, fill=self.fill_color, width=self.line_width
            )
        elif self.current_shape == "circle":
            # Calculate radius for circle (using DDA-like approach)
            radius = math.sqrt((event.x - self.start_x)**2 + (event.y - self.start_y)**2)
            self.temp_shape = self.canvas.create_oval(
                self.start_x - radius, self.start_y - radius,
                self.start_x + radius, self.start_y + radius,
                outline=self.current_color, fill=self.fill_color, width=self.line_width
            )
    
    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            return
        
        # If an item was being moved, save the state
        if self.selected_item and self.current_shape not in ["polygon", "text"]:
            self.save_state()
            return
        
        # Skip for polygon and text (handled by double-click)
        if self.current_shape in ["polygon", "text"]:
            return
        
        # Delete temporary shape
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = None
        
        # Save state before drawing final shape
        self.save_state()
        
        # Draw final shape
        if self.current_shape == "line":
            # DDA Line Algorithm
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y
            
            dx = x2 - x1
            dy = y2 - y1
            
            if abs(dx) > abs(dy):
                steps = abs(dx)
            else:
                steps = abs(dy)
            
            if steps == 0:
                # Just a point
                item = self.canvas.create_line(x1, y1, x1+1, y1, fill=self.current_color, width=self.line_width)
                self.drawn_items.append(item)
                return
                
            x_increment = dx / steps
            y_increment = dy / steps
            
            x, y = x1, y1
            
            points = []
            for i in range(int(steps) + 1):
                points.extend([round(x), round(y)])
                x += x_increment
                y += y_increment
            
            if len(points) >= 4:  # Need at least 2 points (4 coordinates)
                item = self.canvas.create_line(points, fill=self.current_color, width=self.line_width)
                self.drawn_items.append(item)
            
        elif self.current_shape == "rectangle":
            item = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y, 
                outline=self.current_color, fill=self.fill_color, width=self.line_width
            )
            self.drawn_items.append(item)
            
        elif self.current_shape == "oval":
            item = self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y, 
                outline=self.current_color, fill=self.fill_color, width=self.line_width
            )
            self.drawn_items.append(item)
            
        elif self.current_shape == "circle":
            # Calculate radius for circle
            radius = math.sqrt((event.x - self.start_x)**2 + (event.y - self.start_y)**2)
            
            # Draw circle using midpoint circle algorithm
            if radius > 0:
                item = self.canvas.create_oval(
                    self.start_x - radius, self.start_y - radius,
                    self.start_x + radius, self.start_y + radius,
                    outline=self.current_color, fill=self.fill_color, width=self.line_width
                )
                self.drawn_items.append(item)
        
        # Reset starting point
        self.start_x = None
        self.start_y = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
