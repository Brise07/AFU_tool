
class FireCheckResults:

    def __init__(self):
        self.compliance_list = []
        self.calculated_width_list = []
        self.min_required_width = 0
        self.is_public = False

    def add_room_compliance(self, compliance):
        self.compliance_list.append(compliance)

    def add_calculated_width(self, calculated_width):
        self.calculated_width_list.append(calculated_width)

    def get_result_messages(self):
        result_messages = []
        for index, compliance in enumerate(self.compliance_list):
            result_messages.append(self.get_result_message(compliance, index))
        return result_messages

    def get_result_message(self, compliance, index):
        message_color = "black"  
        recommended = 2 if self.is_public else 1.5
        if compliance == 1:
            long_message = (f"Corridor is wide enough according to BR18. "
                        f"Required width is {self.min_required_width} m.\n"
                        f"But it is not compliant with Universal Design principles. "
                        f"The recommended corridor width is {recommended} m.")
            room_color = "yellow"
        elif compliance == 2:
            long_message = f"Corridor is wide enough. Required width is {self.min_required_width} m."
            room_color = "green"
        else:
            long_message = f"Corridor is not wide enough! Required width is {self.min_required_width} m!"
            message_color = "red"
            room_color = "red"
        message = f"Calculated width: {self.calculated_width_list[index]} m"
        return message, message_color, room_color, long_message

  
