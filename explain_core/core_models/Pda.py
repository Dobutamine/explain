import math

class Pda:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # independent properties
        self.length = 10.0              # in mm
        self.diameter = 5.1            # in mm
        self.viscosity = 3.5          # in cP (Pa * s)
        self.velocity = 0
        self.velocity10 = 0

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # dependent properties
        self.res = 1.0                 # resistance in mmHg * s * l-1
        self.raw_flow = 0.0                # in l/s
        self.flow = 0.0            # in m/s
        
        # get a reference to the whole model
        self.model = model
        
        self.initialized = False
        self.delta_p = 0.0
        self.pda = {}
  
    def initialize(self):
        # get a reference to the ductus arteriosus blood connector
        self.pda = self.model.components['DA']
        
        # initialization is now complete
        self.initialized = True
        
    def model_step(self):
        # enable or disable the DA connector depending on the state of the pda model
        self.model.components['DA'].is_enabled = self.is_enabled
        
        # if the Pda model is enabled then initialize the model if not done before, otherwise calculate the resistance of the duct.
        if self.is_enabled:
            if self.initialized:
                self.calculate_resistance()
            else:
                self.initialize()
            
        
    def calculate_resistance(self):
        # calculate the resistance of the ductus arteriousus where
        # the duct is modeled as a perfect tube with a diameter and a length in millimeters
        # the viscosity is in centiPoise
        
        # resistance is calculated using Poiseuille's Law : R = (8 * n * L) / (PI * r^4)
        
        # we have to watch the units carefully where we have to make sure that the units in the formula are 
        # resistance is in mmHg * s / l
        # L = length in meters from millimeters
        # r = radius in meters from millimeters
        # n = viscosity in mmHg * s from centiPoise
        
        # convert viscosity from centiPoise to mmHg * s
        n_mmhgs = self.viscosity * 0.001 * 0.00750062
        
        # convert the length to meters
        length_meters = self.length / 1000.0
        
        # calculate the radius in meters
        radius_meters = (self.diameter / 2) / 1000.0

        # calculate the resistance using Poiseuille's Law, the resistance is now in mmHg * s/mm^3
        self.res = (8.0 * n_mmhgs * length_meters) / (math.pi * math.pow(radius_meters, 4))
        
        # convert resistance of mmHg * s / mm^3 to mmHg *s / l
        self.res = self.res / 1000.0
        
        # transfer the resistance to the ductus arteriosus blood connector and enable flow
        self.pda.no_flow = not self.is_enabled
        self.pda.r_for = self.res
        self.pda.r_back = self.res
        
        # store the pda flow in l / s
        self.flow = self.pda.flow
        
        # calculate the velocity in m/s, for that we have to convert the flow to mm^3/sec
        # velocity = flow_rate (in mm^3/s) / (pi * radius^2)     in m/s
        self.velocity = (self.pda.flow / 1000.0) / (math.pi * math.pow(radius_meters, 2.0))
        self.velocity10 = self.velocity * 10.0