import math


class Ans:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # get a reference to the whole model
        self.model = model

        # define the properties
        self.is_enabled = True
        self.sensors = []
        self.effect_sites = []
        self.ans_inputs = {}

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # define state variables
        self._initialized = False

    def model_step(self):
        if self.is_enabled:
            self.ans_activity()

    def initialize(self):
        # get reference to all the sensors
        for sensor in self.sensors:
            self.ans_inputs[sensor["name"]] = {
                "model": self.model.components[sensor["name"]]
            }
        self._initialized = True


    def ans_activity(self):
       if not self._initialized:
           self.initialize()