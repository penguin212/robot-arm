import Arm

class ArmState:
    def __init__(self, positions = []):
        self.positions = positions
    
    def set_positions(self, arm : Arm):
        self.positions = Arm.get_position()
    
    
    def get_positions(self):
        return self.positions