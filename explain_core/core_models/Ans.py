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
                "ref": effect_site["reference_value"],
                "prev_prop_change": 0.0
            }
        self._initialized = True


    def ans_activity(self):
        if not self._initialized:
           self.initialize()

        # calculate effect on heartrate
        for (_, effector_site) in self.effectors.items():
            # get the sensor value
            sensor_value = (effector_site["sensor"].sensor_output - 50.0)

            # calculate the property change
            prop_change = sensor_value * effector_site["gain"]

            # calculate the new property value
            new_value = effector_site["ref"] + prop_change

            # preserve mass if the property to change is the unstressed volume
            if effector_site["prop"] == "u_vol":
                # change th volume as we shift volume from the u_vol to the vol
                effector_site["model"].vol -= (prop_change - effector_site["prev_prop_change"])
                
                # store the current volume change
                effector_site["prev_prop_change"] = prop_change

            # set the actual property
            setattr(effector_site["model"], effector_site["prop"], new_value)
