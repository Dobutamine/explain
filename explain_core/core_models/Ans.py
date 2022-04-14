import math


class Ans:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # get a reference to the whole model
        self.model = model

        # define the update counters as the ANS doesn't need to be updated every 0.5 ms
        self.update_counter = 0
        self.update_interval = 0.005

        # set the init flag to false
        self.initialized = False

        # define the settings lists
        self.sensors = []
        self.integrators = []
        self.effectors = []

        # define the components
        self.ans_sensors = {}
        self.ans_integrators = {}
        self.ans_effectors = {}

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)

    def model_step(self):
        if self.is_enabled:
            if (self.update_counter >= self.update_interval):
                self.update_counter = 0
                self.ans_activity()

            self.update_counter += self.model.modeling_stepsize

    def initialize(self):
        # initialize the sensors
        for sensor in self.sensors:
            # instantiate a new sensor
            new_sensor = Sensor(self.model, sensor, self.update_interval)

            # add sensor to sensor dictionary
            self.ans_sensors[new_sensor.name] = new_sensor

        # initialize the integrators
        for integrator in self.integrators:
            # instantiate a new sensor
            new_integrator = Integrator(self.model, integrator, self.update_interval)

            # add integrator to integrator dictionary
            self.ans_integrators[new_integrator.name] = new_integrator

        # initialize the effectors
        for effector in self.effectors:
            # instantiate a new sensor
            new_effector = Effector(self.model, effector, self.update_interval)

            # add effector to effector dictionary
            self.ans_effectors[new_effector.name] = new_effector

        # set the initialization flag to true
        self.initialized = True

    def ans_activity(self):
        # only initialize the ANS AFTER everything else
        if not self.initialized:
            self.initialize()

        # get the output of the sensors and feed them into the integrators
        for (_, sensor) in self.ans_sensors.items():
            # get the sensor output
            sensor_output = sensor.update_sensor()

            # apply the sensor output to the correct integrator
            self.ans_integrators[sensor_output[0]].update_integrator(sensor_output[1])

        # get the output of the integrators and feed them into the effectors
        for (_, integrator) in self.ans_integrators.items():
            # get the integrator output
            integrator_output = integrator.get_output()

            # apply the integrator output to the correct effector
            for effector in integrator_output[0]:
                # effector is an object with effector and effect_size 
                self.ans_effectors[effector["effector"]].update_effector(integrator_output[1] * effector["effect_size"])

            # # reset the integrators
            integrator.integrator_output = 0.0

        # process the effectors and apply the effect
        for (_, effector) in self.ans_effectors.items():
            effector.apply_effect()


class Sensor:
    def __init__(self, model, sensor_args, update_interval):
        # store a reference to the complete model
        self.model = model

        # get the update interval
        self.update_interval = update_interval

        # process the sensor argument list
        sensor = sensor_args["sensor"].split(".")
        self.sensor_model = self.model.components[sensor[0]]
        self.sensor_prop = sensor[1]

        # check whether the sensor requires the oxygenation and acidbase model to be active on the sensos
        if (self.sensor_prop == 'po2' or self.sensor_prop == 'pco2' or self.sensor_prop == 'ph'):
            self.sensor_model.oxy_enabled = True
            self.sensor_model.acidbase_enabled = True
        
        # set the rest of the properties
        self.name = sensor_args["name"]
        self.is_enabled = sensor_args["is_enabled"]
        self.setpoint = sensor_args["setpoint"]
        self.amplitude = sensor_args["amplitude"]
        self.sensitivity = sensor_args["sensitivity"]
        self.time_constant = sensor_args["time_constant"]
        self.integrator = sensor_args["integrator"]

        # state variable
        self.sensor_output = 0

    def update_sensor(self):
        # get sensor if enabled
        if (self.is_enabled):
            # get the sensor value
            sensor_value = getattr(self.sensor_model, self.sensor_prop)

            # process the sensor value and generate the sensor output
            activity = ((2 * self.amplitude) / (1 + math.pow(math.e, (sensor_value - self.setpoint) * -self.sensitivity))) - self.amplitude

            # apply the time constant
            self.sensor_output = self.update_interval * ((1 / self.time_constant) * (-self.sensor_output + activity)) + self.sensor_output

            # return the sensor output
            return (self.integrator, self.sensor_output)
        else:
            return (self.integrator, 0.0)

class Integrator:
    def __init__(self, model, integrator_args, update_interval):
        # store a reference to the complete model
        self.model = model

        # get the update interval
        self.update_interval = update_interval

        # process the integrator argument list
        self.name = integrator_args["name"]
        self.is_enabled = integrator_args["is_enabled"]
        self.effectors = integrator_args["effectors"]

        # state variable
        self.integrator_output = 0

    def update_integrator(self, sensor_output):
        self.integrator_output += sensor_output

    def get_output(self):
        return (self.effectors, self.integrator_output)


class Effector:
    def __init__(self, model, effector_args, update_interval):
        # store a reference to the complete model
        self.model = model

        # get the update interval
        self.update_interval = update_interval

        # process the integrator argument list
        self.name = effector_args["name"]
        self.is_enabled = effector_args["is_enabled"]
        self.effect_sites = []
        for effect_site in effector_args["effect_sites"]:
            (site_model, site_prop) = effect_site["effect_site"].split(".")
            self.effect_sites.append({ "model": self.model.components[site_model], "prop": site_prop, "ref": effect_site["ref"]})

        # state variable
        self.effector_output = 0
    
    def update_effector(self, integrator_output):
        self.effector_output = integrator_output

    def apply_effect(self):
        # apply effect
        for effect_site in self.effect_sites:
            new_value = effect_site["ref"] + self.effector_output
            setattr(effect_site["model"], effect_site["prop"], new_value)
        
        # reset the effector output
        self.effector_output = 0

