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
        # get reference to all the sensors
        for effect_site in self.effect_sites:
            (model, prop) = effect_site["target"].split(".")
            self.effectors[effect_site["name"]] = {
                "sensor": self.model.components[effect_site["sensor"]],
                "model": self.model.components[model],
                "prop": prop,
                "gain": effect_site["gain"],
                "ref": effect_site["reference_value"]
                
            }
        print(self.effectors)
        self._initialized = True


    def ans_activity(self):
        if not self._initialized:
           self.initialize()

        # calculate effect on heartrate
        for (_, effector_site) in self.effectors.items():
            # get the sensor value
            sensor_value = (effector_site["sensor"].sensor_output - 50.0)
            # get the gain and reference
            gain = effector_site["gain"]
            ref = effector_site["ref"]
            # apply the effect
            new_value = ref + sensor_value * gain
            setattr(effector_site["model"], effector_site["prop"], new_value)
