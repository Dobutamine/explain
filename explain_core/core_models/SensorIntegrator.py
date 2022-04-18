import math

class SensorIntegrator:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # get a reference to the whole model
        self.model = model

        # properties
        self.name = ""
        self.is_enabled = True
        self.sensors = []
        self.update_interval = 0.05
        self.sensor_output = 0.0
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
          
        # housekeeping
        self._update_counter = 0.0
        self._model_stepsize = self.model.modeling_stepsize
        self._initalized = False
        
    def initialize(self):
      pass


    def model_step(self):
        if self.is_enabled:
            if self._update_counter > self.update_interval:
              self.update_integrator()
              self._update_counter = 0.0
            self._update_counter += self._model_stepsize

    def update_integrator(self):
      if not self._initalized:
        self.initialize

      total_magnitude = 0
      total_output = 0
      for sensor in self.sensors:
        output = self.model.components[sensor["sensor"]].sensor_output * sensor["magnitude"]
        total_magnitude += sensor["magnitude"]
        total_output += output
      
      self.sensor_output = total_output / total_magnitude
      


