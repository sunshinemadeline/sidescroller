
class GameController():
    '''
    Logical representation of a game controller with a flag for each button
    '''
    def __init__(self):
        self.reset()

    def reset(self):
        self.mleft = False
        self.mright = False
        self.jump = False
        self.shoot = False
        self.throw = False