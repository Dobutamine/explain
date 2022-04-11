import math

class Ecls:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        self.vol = 0.0
        self.sweep_gas = 1.5
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the whole model
        self.model = model
        
        self.initialized = False
        self.gas_in = {}
        self.gas_out = {}
        self.gas_lung = {}
        self.gas_valve_in = {}
        self.gas_valve_out = {}
        self.flow_tim = 0
        
    def model_step(self):
        if self.is_enabled:
            if self.initialized:
                self.model_cycle()
            else:
                self.initialize()
    
    def initialize(self):
        self.gas_in = self.model.components['ELGIN']
        self.gas_lung = self.model.components['ELUNG']
        self.gas_out = self.model.components['ELGOUT']
        self.gas_valve_in = self.model.components['ELGIN_ELUNG']
        self.gas_valve_out = self.model.components['ELUNG_ELGOUT']
        
        self.initialized = True
    
    def model_cycle(self):
        # calculate the resistance of the valve depending on the desired sweep gas
        resistance = (self.gas_in.pres - self.gas_lung.pres) / (self.sweep_gas / 60.0)
        resistance = resistance - self.gas_valve_out.r_for
        
        self.gas_valve_in.r_for = resistance
        self.gas_valve_in.r_back = resistance
        
        self.model.components['PUMPOUT'].pres_outside = 100.0
        self.model.components['PUMPIN'].pres_outside = -100.0
        flow_out = self.model.components['PUMPOUT_SUCT'].flow
        self.flow_tim = flow_out
        self.model.components['PUMPIN'].volume_out(flow_out * self.model.modeling_stepsize, self.model.components['SUCT'])
        
