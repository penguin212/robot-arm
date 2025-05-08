import xarm
from Arm import Arm
from ArmState import ArmState
from pynput.keyboard import Key, Listener
import sys
import time


arm = Arm()





claw = xarm.Servo(1) # open [150, 718] closed
servo2 = xarm.Servo(2) # [-170, 1150] 1000 left 220 right use uint_to_int
servo3 = xarm.Servo(3) # [-175, 586]
servo4 = xarm.Servo(4) # [-52, 1000]
servo5 = xarm.Servo(5) # [116, 895]
servo6 = xarm.Servo(6) # [-145, 1142]


# default_pose = [715, 229, 113, 505, 513, 114] #vertical
default_pose = [715, 500, 500, 500, 500, 500] #vertical

default_state = ArmState(default_pose)

open_claw = ArmState([150, None, None, None, None, None])
closed_claw = ArmState([715, None, None, None, None, None])


# arm.off()
arm.set_state(default_state)


closed = True;
def toggleClosed():
    global closed
    closed = not closed
    
input_string = []

def parseStateCommand(command : str):
    try:
        if command[0] == 's':
            arm.addSaveState(command[1])
            print("Added save state: " + command[1])
            return
        if command[0] == 'g':
            print("Go to save state: " + command[1])
            arm.setSaveState(command[1])
            print("Go to save state: " + command[1])
            return
        command = command.split('.')
        if(len(command[0]) != 1): return
        state = [None, None, None, None, None, None]
        state[int(command[0]) - 1] = int(command[1])
        arm.set_state(ArmState(state))
    except KeyboardInterrupt:
        raise KeyboardInterrupt



def on_press(key):
    # print(key)  
    
    global input_string
    
    if key == Key.space:
        toggleClosed()
        arm.set_state(open_claw) if closed else arm.set_state(closed_claw)
    elif key == Key.backspace:
        if input_string != []:
            input_string = input_string[:-1]
        sys.stdout.write("\033[K")
        print(''.join(input_string), end="\r")
    
    elif key == Key.enter:
        parseStateCommand(''.join(input_string))
        input_string = []
        sys.stdout.write("\033[K")
    
    elif key == Key.tab:
        arm.off()
        
    elif str(key).replace("'", "") == 'a':
        print("ASSIST: " + str(arm.set_assist()))
    
    else:
        input_string.append(str(key).replace("'", ""))
        sys.stdout.write("\033[K")
        print(''.join(input_string), end="\r")
            

listener = Listener(on_press=on_press)
listener.start()

timetime = time.time()
left = True
while True:
    # if time.time() - timetime > .5:
    #     timetime = time.time()
    #     if left:
    #         parseStateCommand("3.700")
    #     else:
    #         parseStateCommand("3.300")
    #     left = not left
    
    arm.tick()
    pass
    # print (arm.get_state().get_positions())

