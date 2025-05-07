import xarm
from ArmState import ArmState
import pickle
import os

# servo1 open [150, 718] closed
# servo2 [-170, 1150] 1000 left 220 right use uint_to_int
# servo3 [-170, 1150]
# servo4 [-52, 1000]
# servo5 [116, 895]
# servo6 [-145, 1142]

bounds = [[150,718], [0, 1000], [0, 1000], [0, 1000], [116, 895], [0, 1000]]

def getServo(a):
    return a + 1

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


class Arm:
    def __init__(self):
        num_positions = 4
        self.arm = xarm.Controller('USB')
        self.assist = False
        self.set_position = self.get_state().get_positions()
        self.positions = []
        self.velocities = [0,0,0,0,0,0]
        for i in range(num_positions):
            self.positions.append([])
            self.positions[i] = self.set_position
        self.saved_states = dict()
        if os.path.exists('saved_states.pkl'):
            with open('saved_states.pkl', 'rb') as f:
                self.saved_states = pickle.load(f)
        print('Battery voltage in volts:', self.arm.getBatteryVoltage())
    
    def uint_to_int (self, a : int):
        if a > (65536/2):
            return a - 65536
        else: return a
    
    def get_state(self):
        return ArmState(list(map((lambda x: self.uint_to_int(self.arm.getPosition(x))), list(range(1,7)))))
    
    def set_state(self, state : ArmState, time = 1000):
        for i in range (0,6):
            if(state.positions[i] != None):
                self.set_position[i] = state.positions[i]
                self.arm.setPosition(getServo(i), clamp(self.set_position[i], bounds[i][0], bounds[i][1]), duration=time)
    
    def set_assist(self, assist : bool | None = None):
        if assist == None:
            self.assist = not self.assist
        else:
            self.assist = assist
        return self.assist
    
    def get_velocities(self, lst):
        latest = lst[0]
        oldest = lst[-1]
        vels = []
        for i in range(6):
            vels.append(latest[i] - oldest[i])
        return vels
    
    def get_max_difference(self, lst1, lst2):
        s = 0
        for i in range(len(lst1)):
            s = max(abs(lst1[i] - lst2[i]), s)
        return s
    
    def avg_position(self, lst):
        s = [0,0,0,0,0,0]
        for i in range(len(lst)):
            for j in range(6):
                s[j] += lst[i][j]
        for i in range(6):
            s[i] /= len(lst)
            s[i] = int(s[i])
        return s
    
    def tick(self):
        # print(self.velocities)
        
        self.positions.pop()
        # self.positions.insert(0, self.get_state().get_positions())
        for i in range(10):
            try:
                self.positions.insert(0, self.get_state().get_positions())
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                pass
        # current_state = self.get_state().get_positions()
        for i in range(10):
            try:
                current_state = self.get_state().get_positions()
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                pass
        
        velocities = self.get_velocities(self.positions)
        
        if self.get_max_difference(velocities, self.velocities) > 10:
            self.velocities = velocities
        
        if self.get_max_difference(velocities, [0,0,0,0,0,0]) < 4:
            self.velocities = [0,0,0,0,0,0]
            current_state = self.set_position
        self.set_position = current_state
        
        
        if self.assist:
            current_state[0] = 0
            new_state = list(map(lambda i : current_state[i] + self.velocities[i] * 15, range(6)))
            for i in range(6):
                if new_state[i] < bounds[i][0]:
                    self.velocities[i] = -self.velocities[i]
                elif new_state[i] > bounds[i][1]:
                    self.velocities[i] = -self.velocities[i]
            new_state[0] = None
            self.set_state(ArmState(new_state), time=1000)
        
            
    def addSaveState(self, key : chr, state : ArmState | None = None):
        if state == None: state = self.get_state()
        
        state.positions[0] = None
        self.saved_states[key] = state
        with open('saved_states.pkl', 'wb') as f:
            pickle.dump(self.saved_states, f)
        
    
    def setSaveState(self, key : chr):
        if key in self.saved_states:
            self.set_state(self.saved_states[key])
    
    def getArm(self):
        return self.arm
    
    def off(self):
        self.arm.servoOff()