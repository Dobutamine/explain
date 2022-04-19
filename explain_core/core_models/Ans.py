import math


class Ans:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # get a reference to the whole model
        self.model = model

        # define the properties
        self.is_enabled = True
        self.effect_sites = []
        self.effectors = {}

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # define state variables
        self._initialized = False

    def model_step(self):
        if self.is_enabled:
            self.ans_activity()

    def initialize(self):
        self._initialized = True


    def ans_activity(self):
        if not self._initialized:
           self.initialize()

