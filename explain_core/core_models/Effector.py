class Effector:
    def __init__(self, model, **args):
      # initialize the super class
        super().__init__()

        # get a reference to the whole model
        self.model = model

        # define the properties
        self.is_enabled = True
        self.sensor = "sns"
        self.effect_site = "ecg.heart_rate"
        self.gain = 1.0
        self.reference = 135.0
        self.preserve_mass = False
        self.preserve_mass_from = ""

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # define state variables
        self._initialized = False
        self._sensor_model = {}
        self._effect_site_model = {}
        self._effect_site_prop = {}
        self._pres_mass_model = {}
        self._pres_mass_prop = {}
        self._prop_change = 0
        self._prev_prop_change = 0

    def initialize(self):
      
      # store the references to the correct mmodels
      self._sensor_model = self.model.components[self.sensor]
      if (self.preserve_mass):
        (pres_mass_model, self._pres_mass_prop) = self.preserve_mass_from.split(".")
        self._pres_mass_model = self.model.components[pres_mass_model]

      (effect_site_model, self._effect_site_prop) = self.effect_site.split(".")
      self._effect_site_model = self.model.components[effect_site_model]

      print(self._pres_mass_model)
      print(self._effect_site_model)

      self._initialized = True

    def model_step(self):
      if self.is_enabled:
        self.effector_activity() 

    def effector_activity(self):
      if not self._initialized:
        self.initialize()

      # get the sensor value
      sensor_value = (self._sensor_model.sensor_output - 50.0)

      # calculate the property change
      self._prop_change = sensor_value * self.gain

      if self.preserve_mass:
        # get the current value of the property which is used to conserve the mass
        current_mass_prop = getattr(self._pres_mass_model, self._pres_mass_prop)
        
        # adjust the property
        current_mass_prop -= self._prop_change - self.prev_prop_change

        # store the current prop change
        self.prev_prop_change = self._prop_change

        setattr(self._pres_mass_model, self._pres_mass_prop, current_mass_prop)

      # calculate the new property value
      new_value = self.reference + self._prop_change

      # set the actual property
      setattr(self._effect_site_model, self._effect_site_prop, new_value)