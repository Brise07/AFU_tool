import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
from room import Room
from user_interfaces import ApplicationMainFrame, CollapsibleFrame, UsageCategoryFrame
from check_fire_regulation_compliance import check_fire_regulation
from fire_check_results import FireCheckResults
from get_room_geom import get_rooms
from pdf_export import export_to_pdf
import ifcopenshell


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AFU")
        self.geometry("1200x800")

        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create top frame for controls and check button
        self.top_frame = ttk.Frame(self.main_container)
        self.top_frame.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(self.top_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)

        self.check_fire_regulation_button = ttk.Button(
            button_frame,
            text="Check compliance with Fire Regulation",
            command=self.check_fire_regulation,
            style="Green.TButton",
        )
        self.check_fire_regulation_button.pack(side=tk.TOP)

        # Create Export button
        self.export_button = ttk.Button(
            button_frame,
            text="Export",
            command=self.on_export_to_pdf,
            state=tk.DISABLED,
        )
        self.export_button.pack(fill=tk.X, expand=True, side=tk.TOP, pady=10)

        # Create collapsible frame for controls
        self.controls_frame = CollapsibleFrame(
            self.top_frame, text="Toggle configurations"
        )
        self.controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Top frame for file selection and checkbox
        self.top_frame = ttk.Frame(self.controls_frame.content)
        self.top_frame.pack(fill=tk.X, pady=(5, 10))

        # File selection
        self.file_frame = ttk.LabelFrame(
            self.top_frame, text="IFC File Selection", padding="5"
        )
        self.file_frame.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(
            self.file_frame, textvariable=self.file_path, width=50
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))

        self.browse_button = ttk.Button(
            self.file_frame, text="Browse", command=self.browse_file
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Public building checkbox
        self.public_building = tk.BooleanVar()
        self.public_check = ttk.Checkbutton(
            self.top_frame,
            text="Is the building open to the public\n(e.g. school, library, hospital)?",
            variable=self.public_building,
        )
        self.public_check.pack(side=tk.LEFT, padx=20)

        # Usage category selector
        self.usage_frame = UsageCategoryFrame(self.controls_frame.content)
        self.usage_frame.pack(fill=tk.X, pady=(0, 10))

        # Configure style for green button
        style = ttk.Style()
        style.configure("Green.TButton", background="green", foreground="black")

        # Create ApplicationMainFrame for room visualization
        self.app_frame = ApplicationMainFrame(self.main_container)
        self.app_frame.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select IFC file",
            filetypes=[("IFC files", "*.ifc"), ("All files", "*.*")],
        )
        if not file_path:
            return
        self.file_path.set(file_path)
        try:
            model = ifcopenshell.open(file_path)
            self.rooms = get_rooms(model)
            self.app_frame.room_canvas.set_rooms(self.rooms)
            # Update the room list
            self.app_frame.room_list_frame.update_room_list(
                self.app_frame.room_canvas.rooms
            )
            # Disable the export button when a new file is imported
            self.export_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {str(e)}")

    def check_fire_regulation(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an IFC file first")
            return
        selected_rooms= self.get_selected_rooms_by_names([room.name for room in self.app_frame.room_canvas.get_escape_route_rooms()])
        if not selected_rooms:
            messagebox.showerror("Error", "Please select at least one room")
            return
        self.app_frame.room_canvas.update_room_people()
        result: FireCheckResults = check_fire_regulation(selected_rooms, self.public_building.get(), self.usage_frame.get_selected_category())
        self.result = result
        self.app_frame.show_results(result.get_result_messages())
        self.export_button.config(state=tk.NORMAL)

    def on_export_to_pdf(self):
        export_to_pdf(self)

    def get_selected_rooms_by_names(self, names: List[str]) -> List[Room]:
        selected_rooms = []
        for room in self.rooms:
            room.is_part_of_escape_route = False
            if room.name in names:
                room.is_part_of_escape_route = True
                selected_rooms.append(room)
        return selected_rooms

def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
