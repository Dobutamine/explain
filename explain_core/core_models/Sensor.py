import math

class Sensor:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # get a reference to the whole model
        self.model = model

        # properties
        self.name = ""
        self.is_enabled = False
        self.sensor = "AA.pres"
        self.sensor_model = {}
        self.sensor_prop = {}
        self.setpoint = 53.0
        self.sensitivity = 0.1
        self.time_constant = 1.0
        self.update_interval = 0.05
        self.sensor_output = 0.0
       
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # housekeeping
        self._update_counter = 0.0
        self._model_stepsize = self.model.modeling_stepsize
        self._initialized = False
  
    def initialize(self):
      # process the sensor argument list
      (sensor_model, sensor_prop) = self.sensor.split(".")
      self.sensor_model = self.model.components[sensor_model]
      self.sensor_prop = sensor_prop

      # check whether the sensor requires the oxygenation and acidbase model to be active on the sensos
      if (self.sensor_prop == 'po2' or self.sensor_prop == 'pco2' or self.sensor_prop == 'ph'):
        self.sensor_model.oxy_enabled = True
        self.sensor_model.acidbase_enabled = True

      # flag that the sensor is initialized
      self._initialized = True

    def model_step(self):
        if self.is_enabled:
            if (self._update_counter > self.update_interval):
              self.update_sensor()
              self._update_counter = 0.0
            self._update_counter += self._model_stepsize

    def update_sensor(self):
      # check whether the sensor is initialized
      if not self._initialized:
        self.initialize()

      # get the sensor value
      sensor_value = getattr(self.sensor_model, self.sensor_prop)

      # process the sensor value and generate the sensor output
      activity = (100.0 / (1 + math.pow(math.e, (sensor_value - self.setpoint) * -self.sensitivity)))

      # apply the time constant
      self.sensor_output = self.update_interval * ((1 / self.time_constant) * (-self.sensor_output + activity)) + self.sensor_output


