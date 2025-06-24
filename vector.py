import numpy as np

class Vector:
    def __init__(self, start, end):
        self.start: tuple = start
        self.end: tuple = end
        self.direction = np.array(end) - np.array(start)
        self.length: float= np.linalg.norm(self.direction)

    def get_x_vals(self):
        return [self.start[0], self.end[0]]
    

    def get_y_vals(self):
        return [self.start[1], self.end[1]]
    

    def get_number_of_points_along_line(self, spacing=0.1):
        start = np.array(self.start)
        end = np.array(self.end)

        # Determine number of points
        num_points = max(2, int(self.length / spacing) + 1)  # +1 to include end point
        
        return num_points