import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from vector import Vector
from room import Room



class UsageCategoryFrame(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Usage Category Selection", padding="10")
        self.selected_category = tk.StringVar(value="1")  # Default to category 1
        
        # Create the table header
        headers = [
            "Category",
            "Sleeping\nAccommodations",
            "Knowledge of\nEscape Routes",
            "Self\nRescue",
            "Max People"
        ]
        
        for col, header in enumerate(headers):
            label = ttk.Label(self, text=header, wraplength=100, justify="center")
            label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
        
        # Category data
        categories = [
            ("1", "No", "Yes", "Yes", "No limit"),
            ("2", "No", "No", "Yes", "Max 50"),
            ("3", "No", "No", "Yes", "No limit"),
            ("4", "Yes", "Yes", "Yes", "No limit"),
            ("5", "Yes", "No", "Yes", "No limit"),
            ("6", "Yes/No", "No", "No", "No limit")
        ]
        
        # Create radio buttons and data rows
        for row, (cat, sleep, know, rescue, limit) in enumerate(categories, start=1):
            # Category number and radio button in the same cell
            cat_frame = ttk.Frame(self)
            cat_frame.grid(row=row, column=0, padx=5, pady=2)
            
            cat_label = ttk.Label(cat_frame, text=f"Category {cat}")
            cat_label.pack(side=tk.LEFT, padx=(0, 5))
            
            radio = ttk.Radiobutton(cat_frame, variable=self.selected_category, value=cat)
            radio.pack(side=tk.LEFT)
            
            ttk.Label(self, text=sleep).grid(row=row, column=1, padx=5, pady=2)
            ttk.Label(self, text=know).grid(row=row, column=2, padx=5, pady=2)
            ttk.Label(self, text=rescue).grid(row=row, column=3, padx=5, pady=2)
            ttk.Label(self, text=limit).grid(row=row, column=4, padx=5, pady=2)
        
        # Configure grid weights
        for i in range(5):
            self.grid_columnconfigure(i, weight=1)
            
    def get_selected_category(self) -> int:
        """Get the currently selected category number"""
        return int(self.selected_category.get())

class RoomCanvasItem:
    """
    Represents a room drawn on the canvas, including its Room object,
    drawing logic, and all interaction handlers.
    """
    def __init__(self, room: Room, canvas: tk.Canvas, master: tk.Tk, room_canvas):
        self.room: Room = room
        self.canvas: tk.Canvas = canvas
        self.master: tk.Tk = master
        self.room_canvas = room_canvas
        self.polygon_id: int = None
        self.current_color: str = self.room_canvas.DEFAULT_COLOR
        
        # Draw the room
        self.redraw()
        
    def redraw(self) -> None:
        """Draw or redraw all elements of the room"""
        # Store old polygon_id for rooms dictionary update
        old_polygon_id = self.polygon_id
        
        # Delete old elements if they exist
        self.delete_from_canvas()
        
        # Get points for drawing
        points = []
        for vector in self.room.boundaries:
            points.extend(vector.start)
        
        # Set color based on escape route status
        self.current_color = self.room_canvas.ESCAPE_ROUTE_COLOR if self.room.is_part_of_escape_route else self.room_canvas.DEFAULT_COLOR
        
        # Draw polygon
        self.polygon_id = self.canvas.create_polygon(points, 
                                                   fill=self.current_color, 
                                                   outline="black", 
                                                   tags="room")
        
        # Bind events
        self._bind_events()
        
        # Update the rooms dictionary with the new polygon_id if needed
        if old_polygon_id in self.room_canvas.rooms:
            self.room_canvas.rooms[self.polygon_id] = self.room_canvas.rooms.pop(old_polygon_id)
            
        # Get the main application frame and update room list
        app_frame = self.master.master
        if isinstance(app_frame, ApplicationMainFrame):
            app_frame.room_list_frame.update_room_list(self.room_canvas.rooms)
        
    def delete_from_canvas(self) -> None:
        """Delete all canvas elements associated with this room"""
        if self.polygon_id:
            self.canvas.delete(self.polygon_id)
            
    def _bind_events(self) -> None:
        """Binds all necessary events for room interaction"""
        self.canvas.tag_bind(self.polygon_id, "<Button-1>", self._on_click)
        
    def _on_click(self, event: tk.Event) -> None:
        """Handles click events for the room"""
        if not hasattr(self.canvas, 'dragging') or not self.canvas.dragging:
            # Toggle escape route status
            self.room.is_part_of_escape_route = not self.room.is_part_of_escape_route
            # Update color based on new status
            self.current_color = self.room_canvas.ESCAPE_ROUTE_COLOR if self.room.is_part_of_escape_route else self.room_canvas.DEFAULT_COLOR
            self.canvas.itemconfig(self.polygon_id, fill=self.current_color)
            
            # Get the main application frame and update room list
            app_frame = self.room_canvas._find_app_frame()
            if app_frame:
                app_frame.room_list_frame.update_room_list(self.room_canvas.rooms)
                
            print(f"Room {self.room.name} clicked! Is escape route: {self.room.is_part_of_escape_route}")

    def set_color(self, color: str) -> None:
        """Set the color of the room and update the display"""
        self.current_color = color
        if self.polygon_id:
            self.canvas.itemconfig(self.polygon_id, fill=color)

class ApplicationMainFrame(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        
        # Configure styles for results
        style = ttk.Style()
        style.configure("Black.TLabel", foreground="black")
        style.configure("Red.TLabel", foreground="red")
        
        # Create main container
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main horizontal container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create left side container (for canvas and controls)
        self.left_container = ttk.Frame(self.main_container)
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create room canvas
        self.room_canvas = RoomCanvas(self.left_container)
        self.room_canvas.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # Create control frame below canvas
        self.control_frame = ttk.Frame(self.left_container)
        self.control_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Add control buttons
        self.zoom_in_btn = ttk.Button(self.control_frame, text="Zoom In", 
                                     command=lambda: self.room_canvas.zoom(
                                         self.room_canvas.width/2, 
                                         self.room_canvas.height/2, 
                                         1.1))
        self.zoom_in_btn.pack(side=tk.RIGHT, padx=2)
        
        self.zoom_out_btn = ttk.Button(self.control_frame, text="Zoom Out", 
                                      command=lambda: self.room_canvas.zoom(
                                          self.room_canvas.width/2, 
                                          self.room_canvas.height/2, 
                                          0.9))
        self.zoom_out_btn.pack(side=tk.RIGHT, padx=2)
        
        self.reset_view_btn = ttk.Button(self.control_frame, text="Reset View", 
                                        command=self.room_canvas.reset_view)
        self.reset_view_btn.pack(side=tk.RIGHT, padx=2)
        
        # Create right side container (for Room List and Legend)
        self.right_container = ttk.Frame(self.main_container)
        self.right_container.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Create and pack the color legend frame
        self.room_color_legend_frame = RoomColorLegendFrame(self.right_container)
        self.room_color_legend_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        # Create right side (Room List)
        self.room_list_frame = RoomListFrame(self.right_container, self.room_canvas)
        self.room_list_frame.pack(side=tk.TOP, fill=tk.Y, expand=True)

    def get_selected_rooms(self) -> List[Room]:
        return self.room_canvas.get_selected_rooms()

    def show_results(self, results: List[tuple[str, str, str]]) -> None:
        """Display results in both room list and canvas
        Args:
            results: List of tuples (message, text_color, room_color)
                    Each tuple corresponds to an escape route room in order
        """
        # Get escape route rooms in order
        escape_route_rooms = self.room_canvas.get_escape_route_rooms()
        
        if len(results) != len(escape_route_rooms):
            raise ValueError(f"Number of results ({len(results)}) must match number of escape route rooms ({len(escape_route_rooms)})")
        
        # Update room list results
        messages = []
        for result in results:
            message, text_color, _, _= result
            style = f"{text_color.capitalize()}.TLabel"  # Convert color to style name
            messages.append((message, style))
        self.room_list_frame.update_results_with_style(messages)
        
        # Update canvas colors
        for room, result in zip(escape_route_rooms, results):
            _, _, room_color, _ = result
            # Find the room item in the canvas
            for room_id, room_item in self.room_canvas.rooms.items():
                if room_item.room.name == room.name:
                    self.room_canvas.itemconfig(room_id, fill=room_color)
                    break

class CollapsibleFrame(ttk.Frame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        
        # Create header frame
        self.header = ttk.Frame(self)
        self.header.pack(fill=tk.X)
        
        # Create toggle button
        self.toggle_button = ttk.Button(
            self.header,
            text="▼ " + text,
            command=self.toggle,
            style="Toolbutton"
        )
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Create container frame that will hold the content
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create content frame inside container
        self.content = ttk.Frame(self.container)
        self.content.pack(fill=tk.BOTH, expand=True)
        
        self.is_expanded = True
        
    def toggle(self):
        if self.is_expanded:
            self.container.pack_forget()
            self.toggle_button.configure(text="▶ " + self.toggle_button["text"][2:])
        else:
            self.container.pack(fill=tk.BOTH, expand=True)
            self.toggle_button.configure(text="▼ " + self.toggle_button["text"][2:])
        self.is_expanded = not self.is_expanded

class RoomColorLegendFrame(CollapsibleFrame):
    def __init__(self, master):
        super().__init__(master, text="Toggle Legend")
        
        # Define colors and their explanations
        legend_items = [
            ("red", "Corridor is not wide enough according to BR18 regulations!"),
            ("yellow", "Corridor is wide enough according to BR18 regulations. But it is not compliant with Universal Design principles."),
            ("green", "Corridor is wide enough according to BR18 regulations and Universal Design principles.")
        ]

        # Create labels for each legend item
        for color, text in legend_items:
            frame = ttk.Frame(self.content)
            frame.pack(fill=tk.X, pady=2)

            color_label = ttk.Label(frame, text="■", foreground=color, font=("TkDefaultFont", 12, "bold"))
            color_label.pack(side=tk.LEFT, padx=(0, 5))

            text_label = ttk.Label(frame, text=text, wraplength=300, justify=tk.LEFT)
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

class RoomListFrame(CollapsibleFrame):
    def __init__(self, master, room_canvas):
        super().__init__(master, text="Toggle Rooms")
        self.room_canvas = room_canvas
        self.highlighted_room_id = None  # Only one room can be highlighted at a time
        
        # Configure styles
        style = ttk.Style()
        style.configure("Room.TFrame", background="white")
        style.configure("Highlight.TFrame", background="yellow")
        style.configure("Room.TLabel", background="white")
        style.configure("Highlight.TLabel", background="yellow")
        style.configure("Result.TLabel", foreground="darkgreen")
        style.configure("Error.TLabel", foreground="darkred")
        style.configure("Black.TLabel", foreground="black")
        style.configure("Red.TLabel", foreground="red")
        
        # Create scrollable frame container
        self.scroll_container = ttk.Frame(self.content)
        self.scroll_container.pack(fill=tk.BOTH, expand=True)
        base_width = 400
        # Create scrollable frame with increased width
        self.canvas = tk.Canvas(self.scroll_container, width=base_width)
        scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=base_width)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Store room frames for highlighting
        self.room_frames = {}
        
        # Bind mouse wheel events for scrolling
        self.bind_mouse_wheel(self)
        self.bind_mouse_wheel(self.canvas)
        self.bind_mouse_wheel(self.scrollable_frame)
        
    def bind_mouse_wheel(self, widget):
        """Bind mouse wheel events to the widget and all its children"""
        widget.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        widget.bind("<Button-4>", self._on_mousewheel)    # Linux scroll up
        widget.bind("<Button-5>", self._on_mousewheel)    # Linux scroll down
        
        # Recursively bind to all children
        for child in widget.winfo_children():
            self.bind_mouse_wheel(child)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta < 0:  # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up
            self.canvas.yview_scroll(-1, "units")
            
    def update_room_list(self, rooms):
        """Update the room list display"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.room_frames.clear()
            
        # Add header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Room header (left)
        ttk.Label(header_frame, text="Room", font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT)
        
        # Result header (middle)
        ttk.Label(header_frame, text="Result", font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=(150, 0))
        
        # People header (right)
        ttk.Label(header_frame, text="People", font=("TkDefaultFont", 9, "bold")).pack(side=tk.RIGHT, padx=(0, 10))
        
        ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill=tk.X, padx=5)
        
        # Add rooms sorted by name
        sorted_rooms = sorted(rooms.values(), key=lambda x: x.room.name)
        
        for room_item in sorted_rooms:
            # Create main room frame with default style
            room_frame = ttk.Frame(self.scrollable_frame, style="Room.TFrame", padding=(5, 2))
            room_frame.pack(fill=tk.X, padx=5, pady=1)
            
            # Store frame reference for highlighting
            self.room_frames[room_item.polygon_id] = room_frame
            
            # Left: Room name with optional long name as tooltip
            room_name = room_item.room.name + " " + room_item.room.long_name
            name_text = "→ " + room_name if room_item.room.is_part_of_escape_route else room_name
            name_font = ("TkDefaultFont", 9, "bold") if room_item.room.is_part_of_escape_route else ("TkDefaultFont", 9)
            name_label = ttk.Label(room_frame, text=name_text, font=name_font, style="Room.TLabel")
            name_label.pack(side=tk.LEFT)
            
            people_label = ttk.Label(room_frame, text=str(room_item.room.number_of_people), style="Room.TLabel", width=6)
            people_label.pack(side=tk.RIGHT, padx=(0, 10))

            result_label = ttk.Label(room_frame, text="", style="Room.TLabel", width=22)
            result_label.pack(side=tk.LEFT, padx=(50, 0))
            
            # Make the people count clickable
            def on_click_people(event, room=room_item.room):
                self.edit_people_count(room)
            people_label.bind("<Button-1>", on_click_people)
            
            # Store result label reference
            room_frame.result_label = result_label
            
            # Bind hover events to highlight room
            def on_enter(e, room_id=room_item.polygon_id):
                self.room_canvas.highlight_room(room_id)
                
            def on_leave(e, room_id=room_item.polygon_id):
                self.room_canvas.unhighlight_room(room_id)
            
            # Bind events to all widgets in the room frame
            for widget in (room_frame, name_label, people_label):
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

    def edit_people_count(self, room):
        """Open a dialog to edit the number of people in a room"""
        # Find the ApplicationMainFrame
        app_frame = self.master
        while not isinstance(app_frame, ApplicationMainFrame) and app_frame is not None:
            app_frame = app_frame.master
            
        if not app_frame:
            return
            
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit People Count - {room.name}")
        dialog.geometry("300x100")
        dialog.transient(app_frame)  # Make dialog modal relative to main window
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog on the ApplicationMainFrame
        x = app_frame.winfo_rootx() + (app_frame.winfo_width() - 300) // 2
        y = app_frame.winfo_rooty() + (app_frame.winfo_height() - 100) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Create and pack widgets
        ttk.Label(dialog, text=f"Enter number of people for {room.name}:").pack(pady=5)
        
        entry = ttk.Entry(dialog)
        entry.insert(0, str(room.number_of_people))
        entry.pack(pady=5)
        entry.select_range(0, tk.END)  # Select all text
        entry.focus()  # Give focus to entry
        
        def save_and_close():
            try:
                new_count = int(entry.get())
                if new_count >= 0:
                    room.number_of_people = new_count
                    # Update the room list to show the new count
                    self.update_room_list(self.room_canvas.rooms)
                    dialog.destroy()
                else:
                    tk.messagebox.showerror("Invalid Input", "Please enter a non-negative number.")
            except ValueError:
                tk.messagebox.showerror("Invalid Input", "Please enter a valid number.")
        
        # Bind Enter key to save_and_close
        entry.bind("<Return>", lambda e: save_and_close())
        
        ttk.Button(dialog, text="Save", command=save_and_close).pack(pady=5)

    def highlight_room_frame(self, room_id):
        """Highlight a room frame and scroll it into view"""
        # Remove old highlight
        if self.highlighted_room_id is not None:
            self.unhighlight_room_frame(self.highlighted_room_id)
        
        # Set new highlight
        self.highlighted_room_id = room_id
        
        # Highlight the selected frame
        if room_id in self.room_frames:
            frame = self.room_frames[room_id]
            frame.configure(style="Highlight.TFrame")
            for child in frame.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(style="Highlight.TLabel")
                elif isinstance(child, ttk.Frame):
                    child.configure(style="Highlight.TFrame")
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Label):
                            grandchild.configure(style="Highlight.TLabel")
    
    def unhighlight_room_frame(self, room_id):
        """Remove highlight from a room frame"""
        if room_id in self.room_frames:
            frame = self.room_frames[room_id]
            frame.configure(style="Room.TFrame")
            for child in frame.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(style="Room.TLabel")
                elif isinstance(child, ttk.Frame):
                    child.configure(style="Room.TFrame")
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Label):
                            grandchild.configure(style="Room.TLabel")
        
        if self.highlighted_room_id == room_id:
            self.highlighted_room_id = None

    def update_results_with_style(self, messages):
        """Update result messages for selected rooms with styles
        Args:
            messages (list): List of tuples (message, style)
        """
        # Get escape route rooms
        escape_route_rooms = []
        for room_id, room_item in self.room_canvas.rooms.items():
            if room_item.room.is_part_of_escape_route:
                escape_route_rooms.append(room_id)
        
        if len(messages) != len(escape_route_rooms):
            raise ValueError(f"Number of messages ({len(messages)}) must match number of escape route rooms ({len(escape_route_rooms)})")
        
        # Clear all previous results
        for frame in self.room_frames.values():
            if hasattr(frame, 'result_label'):
                frame.result_label.configure(text="", style="Room.TLabel")
        
        # Update results for escape route rooms
        for room_id, (message, style) in zip(escape_route_rooms, messages):
            if room_id in self.room_frames:
                frame = self.room_frames[room_id]
                if hasattr(frame, 'result_label'):
                    frame.result_label.configure(text=message, style=style)

class RoomCanvas(tk.Canvas):
    # Color constants
    DEFAULT_COLOR = "lightgray"
    ESCAPE_ROUTE_COLOR = "lightblue"
    HIGHLIGHT_COLOR = "yellow"
    
    def __init__(self, master, width: int=800, height: int=600):
        super().__init__(master, width=width, height=height, bg="white")
        self.width = width
        self.height = height
        
        self.rooms: Dict[int, RoomCanvasItem] = {}
        
        # Initialize view transformation variables
        self.zoom_scale: float = 1.0
        self.base_zoom_scale: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.last_x: float = 0.0
        self.last_y: float = 0.0
        self.dragging: bool = False
        
        # Bind events
        self.bind("<ButtonPress-2>", self.start_drag)
        self.bind("<B2-Motion>", self.drag)
        self.bind("<ButtonRelease-2>", self.end_drag)
        self.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down
        
        # Bind hover events for rooms
        self.tag_bind("room", "<Enter>", self._on_room_enter)
        self.tag_bind("room", "<Leave>", self._on_room_leave)

    def _find_app_frame(self):
        """Find the ApplicationMainFrame by traversing up the widget hierarchy"""
        widget = self
        while widget is not None and not isinstance(widget, ApplicationMainFrame):
            widget = widget.master
        return widget

    def _on_room_enter(self, event):
        """Handle mouse enter event for a room"""
        # Find which room was entered
        room_id = self.find_closest(self.canvasx(event.x), self.canvasy(event.y))[0]
        if room_id in self.rooms:
            # Get the main application frame and highlight the corresponding row
            app_frame = self._find_app_frame()
            if app_frame:
                app_frame.room_list_frame.highlight_room_frame(room_id)
    
    def _on_room_leave(self, event):
        """Handle mouse leave event for a room"""
        # Find which room was left
        room_id = self.find_closest(self.canvasx(event.x), self.canvasy(event.y))[0]
        if room_id in self.rooms:
            # Get the main application frame and unhighlight the corresponding row
            app_frame = self._find_app_frame()
            if app_frame:
                app_frame.room_list_frame.unhighlight_room_frame(room_id)

    def highlight_room(self, room_id):
        """Highlight a room on the canvas"""
        if room_id in self.rooms:
            self.itemconfig(room_id, fill=self.HIGHLIGHT_COLOR)
    
    def unhighlight_room(self, room_id):
        """Remove highlight from a room on the canvas"""
        if room_id in self.rooms:
            room = self.rooms[room_id].room
            color = self.ESCAPE_ROUTE_COLOR if room.is_part_of_escape_route else self.DEFAULT_COLOR
            self.itemconfig(room_id, fill=color)

    def set_rooms(self, rooms: List[Room]) -> None:
        """Sets the rooms to be displayed on the canvas"""
        self.delete("all")
        self.rooms.clear()
        
        # Find the bounds of all rooms
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        self.original_rooms= rooms
        
        for room in rooms:
            for vector in room.boundaries:
                min_x = min(min_x, vector.start[0], vector.end[0])
                min_y = min(min_y, vector.start[1], vector.end[1])
                max_x = max(max_x, vector.start[0], vector.end[0])
                max_y = max(max_y, vector.start[1], vector.end[1])
        
        # Calculate the scale to fit in canvas with padding
        width = max_x - min_x
        height = max_y - min_y
        
        # Add 10% padding
        padding = 0.1
        canvas_width = self.width * (1 - 2 * padding)
        canvas_height = self.height * (1 - 2 * padding)
        
        scale_x = canvas_width / width if width > 0 else 1.0
        scale_y = canvas_height / height if height > 0 else 1.0
        initial_scale = min(scale_x, scale_y)
        
        # Calculate center offset to position rooms in middle of canvas
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        offset_x = self.width / 2 - center_x * initial_scale
        offset_y = self.height / 2 - center_y * initial_scale
        
        # Transform and add rooms
        for room in rooms:
            transformed_vectors = []
            for vector in room.boundaries:
                # Flip Y coordinates by subtracting from canvas height
                start = (
                    vector.start[0] * initial_scale + offset_x,
                    self.height - (vector.start[1] * initial_scale + offset_y)  # Flip Y coordinate
                )
                end = (
                    vector.end[0] * initial_scale + offset_x,
                    self.height - (vector.end[1] * initial_scale + offset_y)    # Flip Y coordinate
                )
                transformed_vectors.append(Vector(start, end))
            
            transformed_room = Room(
                room.name,
                room.long_name,
                room.level,
                transformed_vectors,
                room.is_part_of_escape_route,
                room.number_of_people
            )
            self.add_room(transformed_room)
            
        # Store the scale for future use
        self.zoom_scale = initial_scale
        self.base_zoom_scale = initial_scale
        
        # Update the room list in the main application frame
        app_frame = self._find_app_frame()
        if app_frame:
            app_frame.room_list_frame.update_room_list(self.rooms)

    def update_room_people(self):
        i=0
        for room in self.rooms.values():
            self.original_rooms[i].number_of_people = room.room.number_of_people
            i+=1

    def add_room(self, room: Room) -> None:
        """Adds a Room object to the canvas"""
        room_item = RoomCanvasItem(room, self, self.master, self)  # Pass self as room_canvas
        self.rooms[room_item.polygon_id] = room_item

    def get_escape_route_rooms(self) -> List[Room]:
        """Returns a list of Room objects that are part of the escape route."""
        return [room.room for room in self.rooms.values() if room.room.is_part_of_escape_route]

    def start_drag(self, event: tk.Event) -> None:
        """Start canvas dragging"""
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
        
    def drag(self, event: tk.Event) -> None:
        """Handle canvas dragging"""
        if not self.dragging:
            return
            
        # Calculate the distance moved
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        # Update the offset
        self.offset_x += dx
        self.offset_y += dy
        
        # Move all canvas objects
        self.move("all", dx, dy)
        
        # Update last position
        self.last_x = event.x
        self.last_y = event.y
        
    def end_drag(self, event: tk.Event) -> None:
        """End canvas dragging"""
        self.dragging = False

    def on_mousewheel(self, event: tk.Event) -> None:
        """Handle mouse wheel for zooming"""
        # Get the mouse position
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        
        # Determine zoom direction
        if event.num == 5 or event.delta < 0:  # Zoom out
            factor = 0.9
        else:  # Zoom in
            factor = 1.1
            
        self.zoom(x, y, factor)
        
    def zoom(self, x: float, y: float, factor: float) -> None:
        """Zoom the canvas around a point"""
        # Update scale
        self.zoom_scale *= factor
        
        # Scale all objects relative to the zoom point
        self.scale("all", x, y, factor, factor)
        
        # Update text sizes - use list to avoid dictionary modification during iteration
        room_items = list(self.rooms.values())
        for room_item in room_items:    
            # Update room's stored center position
            if room_item.polygon_id:
                coords = self.coords(room_item.polygon_id)
                if coords and len(coords) >= 4:  # Make sure we have at least 2 points (4 coordinates)
                    room_item.center_x = sum(coords[::2]) / (len(coords[::2]))
                    room_item.center_y = sum(coords[1::2]) / (len(coords[1::2]))
        
    def reset_view(self) -> None:
        """Reset view to original position and scale"""
        # Reset transformation variables
        self.zoom_scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # Delete all current objects
        self.delete("all")
        
        # Redraw all rooms
        for room_item in list(self.rooms.values()):
            self.add_room(room_item.room)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None