# Velocity, Direction classification
# NOTE This file Does Not Know about Drawing and any logic rather than physics

import time
from .config import Config
from line_profiler import profile

class Engine:
    def __init__(self):
        self.prev_time = time.time()
        self.prev_position = None
        self.smooth_x = None
        self.smooth_y = None
        self.smooth_z = None
        self.frame_count = 0
        self.detection = []
        
    def exponential_moving_avarage(self, new_value, smoothing_value)->float:
        if smoothing_value is None:
            smoothing_value = new_value
        else:
            smoothing_value = Config.EMA_ALFA*new_value + (1-Config.EMA_ALFA)*smoothing_value
        return smoothing_value
    
    def smoothing(self, velocity_vector)->tuple:
        vx , vy, vz = velocity_vector
        self.smooth_x = self.exponential_moving_avarage(vx, self.smooth_x)
        self.smooth_y = self.exponential_moving_avarage(vy, self.smooth_y)
        self.smooth_z = self.exponential_moving_avarage(vz, self.smooth_z)
        return (self.smooth_x, self.smooth_y, self.smooth_z)
    
    #Just updating the object data to latest one
    def update(self, detection, frame_index):
        self.detection = detection
        if frame_index % Config.FRAME_SKIP != 0:
            self.prev_time = time.time()

    @profile
    def speed(self, current_position, current_time)-> tuple:
        '''
        ### Work is to only calculte speed and smooth the postions & velocity\n
        #### Return a Tuple with (speed, position vector, velocity vector)
            * speed -> int, 
            * postion change -> tuple,
            * velocity change -> tuple
        '''
        position_vector = []
        velocity_vector = []
        dt = current_time - self.prev_time
        if not self.prev_position is None:
            for new_asix, prev_axis in zip(current_position, self.prev_position):
                change_axis = new_asix - prev_axis
                position_vector.append(change_axis)
                velocity_vector.append(change_axis/dt)
            velocity_vector = self.smoothing(velocity_vector)
        speed = (velocity_vector[0]**2 + velocity_vector[1]**2 + velocity_vector[2]**2)**(1/2)
        position_vector = tuple(position_vector)
        velocity_vector = tuple(velocity_vector)
        return (speed, position_vector, velocity_vector)
    
    @profile
    def direction(self, velocity_vector)->str:
        '''here the decision is decided'''
        vx, vy, vz = velocity_vector
        direction = None
        dominated_direction = max(abs(vx), abs(vy), abs(vz))

        # NOTE Decision Tree
        if dominated_direction == abs(vx):
            if vx < 0:
                direction = 'Left'
            else:
                direction = "Right"
        elif dominated_direction == abs(vy):
            if vy < 0:
                direction = "Up"
            else:
                direction = "Down"
        else:
            if vz < 0:
                direction = "Toward the camera"
            else:
                direction = "Away from Camera"
        return direction
    
    @profile
    def classifier(self)-> str:
        # NOTE : only operating on the wrist for the combined hand motion
        hands = self.detection
        direction = ""

        # NOTE Only operate on one hand in a frame
        wlm = hands.hand_world_landmarks[0] # using world hand landmarks
        current_position = (wlm[0].x, wlm[0].y, wlm[0].z)
        current_time = time.time()
        dt = current_time - self.prev_time
        if self.prev_position == None:
            self.prev_position = current_position
            self.prev_time = current_time
            direction = "Stable"
        else:
            speed, _, velocity_vector = self.speed(current_position, current_time)
            self.prev_position = current_position
            self.prev_time = current_time
            if speed > Config.THRESHOLD:
                direction = self.direction(velocity_vector)
            else:
                direction = "Stable"

            # Debuging lines 
            print(f"dt: {dt:.5f}, vx: {velocity_vector[0]:.5f}, vy: {velocity_vector[1]:.5f}, vz: {velocity_vector[2]:.5f}, speed: {speed:.5f}")

        return direction
    