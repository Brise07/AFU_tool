import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
import matplotlib.pyplot as plt
import numpy as np
from room import Room
from vector import Vector
from typing import List
# Load the IFC model
#model = ifcopenshell.open("Music_box_IFC4_Reference_view_highLoD.ifc")

# Set up geometry settings
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)

if __name__ == "__main__":
    # Prepare plot
    plt.figure(figsize=(10, 8))
    plt.title("2D Room boundariess from IfcSpace geometry")
    plt.xlabel("X (mm or model units)")
    plt.ylabel("Y (mm or model units)")
    plt.grid(True)


def draw_plt():
    plt.legend()
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

def get_boundaries(shape) -> List[Vector]:
    verts = np.array(shape.geometry.verts).reshape(-1, 3)

    # Get lowest Z level (floor level)
    min_z = np.min(verts[:, 2])

    # Extract (x, y) points at the base
    boundaries = verts[verts[:, 2] == min_z][:, :2]

    # Close the loop if not already
    if not np.array_equal(boundaries[0], boundaries[-1]):
        boundaries = np.vstack([boundaries, boundaries[0]])

    # Convert points to Vector objects
    vectors = []
    for i in range(len(boundaries) - 1):
        start = tuple(boundaries[i])
        end = tuple(boundaries[i + 1])
        vectors.append(Vector(start, end))

    return vectors

def get_rooms(model) -> List[Room]:
    spaces = model.by_type("IfcSpace")

    rooms = []
    for space in spaces:

        level = None
        try:
            shape = ifcopenshell.geom.create_shape(settings, space)
            
            boundaries= get_boundaries(shape)
            room_name = space.Name
            room_longname = ifcopenshell.util.selector.get_element_value(space, "LongName")
           
            level = "Unknown"
            rooms.append(Room(name=room_name, long_name=room_longname, level=level, boundaries=boundaries))

            space = model.by_type("IfcSpace")[0]  # Just take one space to inspect



            # print("=== IFCSpace direct attributes ===")
            # for attr in dir(space):
            #     if not attr.startswith("__") and not callable(getattr(space, attr)):
            #         print(f"{attr}: {getattr(space, attr)}")

        except Exception as e:
            print(f"Error processing room {space.GlobalId}: {e}")
    
    return rooms

def get_level_from_boundary(space):
    for rel in space.BoundedBy:
        if rel.is_a("IfcRelSpaceBoundary"):
            level_name = rel.Name
            if level_name:  # Non-empty
                return level_name
    return None

def print_all_properties(space):
    for definition in space.IsDefinedBy:
        if definition.is_a("IfcRelDefinesByProperties"):
            prop_set = definition.RelatingPropertyDefinition
            if prop_set.is_a("IfcPropertySet"):
                print(f"Property Set: {prop_set.Name}")
                for prop in prop_set.HasProperties:
                    print(f"  - {prop.Name}: {getattr(prop, 'NominalValue', None)}")


# storeys = model.by_type("IfcBuildingStorey")

# for storey in storeys:
#     print(f"Storey: {storey.Name}")
#     for rel in model.by_type("IfcRelContainedInSpatialStructure"):
#         if rel.RelatingStructure == storey:
#             for elem in rel.RelatedElements:
#                 if elem.is_a("IfcSpace"):
#                     print(f"  - Space: {elem.Name}")


if __name__ == "__main__":
    rooms = get_rooms()

    # Use a colour map (e.g., 'tab20') to get distinct colours
    cmap = plt.get_cmap('tab20')
    num_rooms = len(rooms)

    for idx, room in enumerate(rooms):
        color = cmap(idx % 20)  # Loop within 20 colours if more rooms
        label_added = False  # Flag to avoid duplicate labels in legend

        for boundary in room.boundaries:
            x = [boundary.start[0], boundary.end[0]]
            y = [boundary.start[1], boundary.end[1]]

            if not label_added:
                plt.plot(x, y, color=color)
                # label_added = True
            else:
                plt.plot(x, y, color=color)

    # plt.legend()
    draw_plt()


