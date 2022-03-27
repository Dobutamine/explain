import math

class Gasexchanger:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        self.flux_o2 = 0
        self.flux_co2 = 0
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the model
        self.model = model
        
        self.initialized = False
        
        self.update_interval = 0.015
        self.update_counter = 0
        self.modeling_stepsize = 0.0005
        
        self.dif_o2_fac = 1.0
        self.dif_co2_fac = 1.0
        # self.initialize()
  
    def model_step(self):
        if self.is_enabled:
            if (self.initialized == False):
                self.initialize()
            self.exchange_gas()

    def initialize (self):
        self.comp_blood = self.model.components[self.comp_blood]
        self.comp_gas = self.model.components[self.comp_gas]
        # activate the oxygenation and acidbase capabilities of the compartments
        self.comp_blood.oxy_enabled = True
        self.comp_blood.acidbase_enabled = True
        
        self.modeling_interval = self.model.modeling_stepsize
        self.initialized = True
        
    def exchange_gas(self):
        # calculate the o2 and co2 flux
        self.flux_o2 = (self.comp_blood.po2 - self.comp_gas.po2) * (self.dif_o2 * self.dif_o2_fac) * self.modeling_interval
        self.flux_co2 = (self.comp_blood.pco2 - self.comp_gas.pco2) * (self.dif_co2 * self.dif_co2_fac) * self.modeling_interval
        
        # change the oxygen content of the blood_compartment
        new_to2 = ((self.comp_blood.to2 * self.comp_blood.vol) - self.flux_o2) / self.comp_blood.vol
        if (new_to2 < 0):
            new_to2 = 0
        self.comp_blood.to2 = new_to2
        
        new_tco2 = ((self.comp_blood.tco2 * self.comp_blood.vol) - self.flux_co2) / self.comp_blood.vol
        if (new_tco2 < 0):
            new_tco2 = 0
        self.comp_blood.tco2 = new_tco2
        
        # change the oxygen and co2 content of the gas_compartment
        self.comp_gas.exchange_gas(self.flux_o2, self.flux_co2)
            


        
            
        
        
    
    