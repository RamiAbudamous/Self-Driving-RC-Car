import config
# speed detector functions
def timer_tick(self, timer):
    velocity = config.VELOCITY_CONSTANT_MULT*self.rotations

    print(f"The velocity was {velocity}cm/s, ({self.rotations} rotations) ")
    if velocity > self.max_velocity:
        # print(f"velocity > max velocity ({velocity}>{self.max_velocity})")
        self.max_velocity = velocity

    self.velocity = velocity
    self.rotations=0

def isr(self, p):
    #print("interrupted")
    self.rotations+=1