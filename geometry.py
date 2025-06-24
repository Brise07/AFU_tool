import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class Line:
    start: tuple
    end: tuple
    length: float

def start_end_to_x_y(start_point, end_point):
    x_values = [start_point[0], end_point[0]]
    y_values = [start_point[1], end_point[1]]
    return x_values, y_values

def x_y_to_start_end(x_values, y_values):
    start_point = [x_values[0], y_values[0]]
    end_point = [x_values[1], y_values[1]]
    return start_point, end_point

def create_line(start_point, direction, length):
    # Calculate the end point by scaling the direction by the length
    direction = direction / np.linalg.norm(direction)  # Normalize to make it a unit vector
    end_point = start_point + direction * length

    # Extract the x and y coordinates for plotting
    x_values = [start_point[0], end_point[0]]
    y_values = [start_point[1], end_point[1]]

    return x_values, y_values

def find_line_middle(x_values, y_values):
    start_point = np.array([x_values[0], y_values[0]])
    end_point = np.array([x_values[1], y_values[1]])

    return (start_point + end_point) / 2

#Divide a Line into Points
def cut_up_line(x_values, y_values, num_points, margin_ratio=0.05):
    start_point = np.array([x_values[0], y_values[0]])
    end_point = np.array([x_values[1], y_values[1]])

    # Compute the direction vector of the line
    direction = end_point - start_point
    line_length = np.linalg.norm(direction)
    direction_unit = direction / line_length

    # Apply margins to both ends
    margin = min(0.15, margin_ratio * line_length)
    new_start = start_point + direction_unit * margin
    new_end = end_point - direction_unit * margin

    return np.linspace(new_start, new_end, int(num_points))

#Returns the intersection point if the ray intersects the segment, else None.
def intersect_ray_with_segment(line_start, line_end, seg_start, seg_end):

    ray_origin = np.array(line_start)
    ray_dir =  np.array(line_end) - np.array(line_start)
    ray_dir = ray_dir / np.linalg.norm(ray_dir)  # Normalize to make it a unit vector

    seg_start = np.array(seg_start)
    seg_end = np.array(seg_end)

    v1 = ray_origin - seg_start
    v2 = seg_end - seg_start
    v3 = np.array([-ray_dir[1], ray_dir[0]])

    dot = np.dot(v2, v3)
    if abs(dot) < 1e-8:
        return None  # parallel
    
    # Convert to 3D vectors to avoid the deprecation warning
    v1_3d = np.append(v1, 0)
    v2_3d = np.append(v2, 0)

    cross = np.cross(v2_3d, v1_3d)
    t1 = cross[2] / dot
    t2 = np.dot(v1, v3) / dot

    if float(t1) >= 0 and 0 <= float(t2) <= 1:
        return ray_origin + t1 * ray_dir  # intersection point
    return None


#Define lines starting from perpendicular line and calculate the length
def perpendicular_lines(x_values, y_values, num_points, walls):
    # Compute original line direction
    start_point = np.array([x_values[0], y_values[0]])
    end_point = np.array([x_values[1], y_values[1]])
    direction = end_point - start_point
    direction = direction / np.linalg.norm(direction)

    # Compute perpendicular directions
    dir1 = np.array([direction[1], -direction[0]])
    dir2 = -dir1

    # Cut the main line into points
    points = cut_up_line(x_values, y_values, num_points)
    print(f"🔍 Cut {len(points)} points from the main line")

    perpendicular_lines = []
    i = 1

    for point in points:
        intersections = []

        # Check intersections in both directions
        length = 100

        for perp_dir in [dir1, dir2]:
            ray_end = point + perp_dir * length
            closest_intersection = None
            min_distance = np.inf

            # Iterate over walls to find intersections
            for wall_start, wall_end in walls:
                intersection = intersect_ray_with_segment(point, ray_end, wall_start, wall_end)
                if intersection is not None:
                    distance = np.linalg.norm(intersection - point)
                    if distance < min_distance:
                        min_distance = distance
                        closest_intersection = intersection

            if closest_intersection is not None:
                intersections.append(closest_intersection)

        # Only draw if we have both sides
        if len(intersections) == 2:
            line_start, line_end = intersections
        elif len(intersections) == 1:
            line_start = point
            line_end = intersections[0]
        else:
            print(f"⚠️ No intersections found for point {point}")
            line_start = point + dir2 * length
            line_end = point + dir1 * length

        line_length = np.linalg.norm(line_end - line_start)
        perpendicular_lines.append(Line(start=tuple(line_start), end=tuple(line_end), length=line_length))
        i += 1
    
    #print(f"✅ Found {len(perpendicular_lines)} perpendicular lines")

    return perpendicular_lines



def perpendicular_lines_from_vector(vector, num_points, walls, offset_ratio):
    # """
    # Given a vector, draws lines to the left side at evenly spaced intervals.
    # Starts slightly after the vector's start point to avoid immediate intersection.
    # """

    start_point = np.array(vector.start)
    end_point = np.array(vector.end)
    direction = end_point - start_point
    norm = np.linalg.norm(direction)

    if norm == 0:
        raise ValueError("Vector has zero length.")

    unit_direction = direction / norm

    # Left-direction vector (90° CCW)
    left_dir = np.array([-unit_direction[1], unit_direction[0]])

    # Offset from the true start point
    offset_distance = offset_ratio * norm
    adjusted_start = start_point #+ unit_direction * offset_distance
    adjusted_end = end_point

    # Cut line into evenly spaced points
    x_values = [adjusted_start[0], adjusted_end[0]]
    y_values = [adjusted_start[1], adjusted_end[1]]
    points = cut_up_line(x_values, y_values, num_points)
    #print(f"Cut {len(points)} points from adjusted vector")

    perpendiculars = []

    for point in points:
        ray_end = point + left_dir * 9999999999999999  # arbitrary large length to find wall
        closest_intersection = None
        min_distance = np.inf

        # Check against all walls
        for wall_start, wall_end in walls:
            intersection = intersect_ray_with_segment(point, ray_end, wall_start, wall_end)
            
            # Check if the intersection is the same as the ray's starting point
            if intersection is not None and not np.allclose(intersection, point):
                distance = np.linalg.norm(intersection - point)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = intersection

        if closest_intersection is not None:
            line_start = point
            line_end = closest_intersection
            line_length = np.linalg.norm(line_end - line_start)
            perpendiculars.append(Line(start=tuple(line_start), end=tuple(line_end), length=line_length))
        else:
                print(f"No intersection found to the left from point {point}")

    #print(f"Found {len(perpendiculars)} left-side perpendicular lines")
    return perpendiculars


def find_shortest_line(lines):
    return min(lines, key=lambda line: line.length)

def find_longest_line(lines):
    return max(lines, key=lambda line: line.length)

if __name__ == "__main__":
    #Create walls
    walls = [
        (np.array([2, 0]), np.array([2, 10])),
        (np.array([-1, 0]), np.array([2, 0])),
        (np.array([-1, 0]), np.array([-1, 8])),
        (np.array([-1, 8]), np.array([-5, 8])),
        (np.array([-5, 10]), np.array([-5, 8])),
        (np.array([-5, 10]), np.array([2, 10])),
    ]

    # Define the start point (x0, y0)
    start_point = np.array([0, 0])

    # Define the direction as a unit vector 
    direction = np.array([0, 1])  
    direction = direction / np.linalg.norm(direction)  # Normalize to make it a unit vector

    # Define the length of the line
    length = 10

    #Define line and midpoint
    line1_x_values, line1_y_values = create_line(start_point, direction, length)
    midpoint = find_line_middle(line1_x_values, line1_y_values)

    num_points = 20
    perpendicular_lines_list = perpendicular_lines(line1_x_values, line1_y_values, num_points, walls)

    shortest_line = find_shortest_line(perpendicular_lines_list)
    longest_line = find_longest_line(perpendicular_lines_list)
    longest_x_values, longest_y_values = start_end_to_x_y(longest_line.start, longest_line.end)

    for i in range(10):
        perpendicular_lines_list_new = perpendicular_lines(longest_x_values, longest_y_values, 20, walls)

        perpendicular_lines_list = perpendicular_lines_list + perpendicular_lines_list_new

        shortest_line = find_shortest_line(perpendicular_lines_list)
        longest_line = find_longest_line(perpendicular_lines_list_new)
        longest_x_values, longest_y_values = start_end_to_x_y(longest_line.start, longest_line.end)

        print("Length of the shortest line:", shortest_line.length)
        print("Length of the longest line:", longest_line.length, longest_line.start, longest_line.end)
        print('Number of lines:', len(perpendicular_lines_list))


    ###### Plotting
    plt.axis("equal")
    plt.grid(True)


    # Plot the lines
    for i, line in enumerate(perpendicular_lines_list):
        x_vals, y_vals = start_end_to_x_y(line.start, line.end)
        if i == 0:
            plt.plot(x_vals, y_vals, color='blue', label='Perpendicular lines')
        else:
            plt.plot(x_vals, y_vals, color='blue')


    # for line in perpendicular_lines_list_new.values():
    #     x_vals, y_vals = start_end_to_x_y(line.start, line.end)
    #     plt.plot(x_vals, y_vals, color='pink') 

    plt.plot(line1_x_values, line1_y_values, color='red', label='Starting line')

    #Plot the walls
    for idx, (start, end) in enumerate(walls):
        wall_x = [start[0], end[0]]
        wall_y = [start[1], end[1]]
        if idx == 0:
            plt.plot(wall_x, wall_y, color='purple', linestyle='--', linewidth=2, label='Walls')
        else:
            plt.plot(wall_x, wall_y, color='purple', linestyle='--', linewidth=2)


    # # Plot the midpoint
    # plt.scatter(midpoint[0], midpoint[1], color='red', label="Midpoint")

    # Add labels and title
    plt.xlabel('X-axis (m)')
    plt.ylabel('Y-axis (m)')

    # Show the plot
    plt.legend()
    plt.show()