import math


class Ans:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # get a reference to the whole model
        self.model = model

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)

    def model_step(self):
        if self.is_enabled:
            pass

    def initialize(self):
        pass

    def ans_activity(self):
       pass