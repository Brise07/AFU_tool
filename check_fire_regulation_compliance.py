import ifcopenshell
import ifcopenshell.geom

### Import the custom functions
from geometry import (
    find_shortest_line,
    perpendicular_lines_from_vector,
)

from typing import List
from room import Room
from fire_check_results import FireCheckResults 

# Load the IFC model
model = ifcopenshell.open("Music_box_Reference_view.ifc")

# Set up geometry settings
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

def get_room_compliance(calculated_width, min_required_width, is_public):

    if min_required_width <= calculated_width:
        if (is_public and calculated_width <= 2) or (not is_public and calculated_width <= 1.5):
            compliance = 1
        else:
            compliance = 2
    else:
        compliance = 0

    return compliance

def check_fire_regulation(rooms:List[Room], is_public, use_category):
    result = FireCheckResults()

    for room in rooms:
        
        if not room.is_part_of_escape_route:
            continue

        selected_boundaries = room.boundaries

        # Convert boundary lines to walls
        walls = []
        for boundary in selected_boundaries:
            walls.append((boundary.start, boundary.end))

        # Define number of points and offset to cut the boundary lines
        offset = 0.1
        all_perpendicular_lines_list = []

        for boundary in selected_boundaries:
            num_points = boundary.get_number_of_points_along_line()
            boundary_x_values = boundary.get_x_vals()
            boundary_y_values = boundary.get_y_vals()

            perpendicular_lines_list = perpendicular_lines_from_vector(
                boundary, num_points, walls, offset
            )
            all_perpendicular_lines_list.extend(perpendicular_lines_list)

        shortest_line = find_shortest_line(
            [line for line in all_perpendicular_lines_list if line.length > 0.3] #TODO: 0.3 parameter comes from user.
        )
        calculated_min_corr_width = round(float(shortest_line.length), 2)


        min_width_fire = room.get_required_min_width_fire(use_category) 
        
        room_compliance = get_room_compliance(calculated_min_corr_width, min_width_fire, is_public)
        result.add_room_compliance(room_compliance)
        result.add_calculated_width(calculated_min_corr_width)
        result.min_required_width = min_width_fire
        result.is_public = is_public
        print(f"Room {room.name} compliance: {room_compliance}")

    return result

      

        
