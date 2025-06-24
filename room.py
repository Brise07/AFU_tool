import matplotlib.pyplot as plt
from typing import List
from vector import Vector

class Room:

    def __init__(
        self, name: str, long_name: str, level, boundaries=[], is_part_of_escape_route=False, number_of_people = 0
    ):
        self.name : str = name
        self.long_name: str = long_name
        self.level : str = level
        self.boundaries : List[Vector] = boundaries
        self.is_part_of_escape_route = is_part_of_escape_route
        self.number_of_people = number_of_people


    def add_to_plt(self):
        for i in range(len(self.boundaries)):
            vector = self.boundaries[i]
            
            # Plot the vector as a line
            plt.plot(
                vector.get_x_vals(),
                vector.get_y_vals(),
                label=f"{i}",
                linewidth=1.5,
            )
            
            # # Plot a red dot at the start of the vector
            # plt.plot(
            #     vector.start[0],
            #     vector.start[1],
            #     'ro'  # red dot
            # )

    
    def get_required_min_width_fire(self, use_category):
        if use_category not in [1,2,3,5] or self.number_of_people <= 150:
            return 1.3
        else:
            return (self.number_of_people * 10) / 1000

    def requirement1(self, req1, number_of_people):
        min_width = Room.check_amount_of_people(self, number_of_people)
        return min_width <= req1
    
    