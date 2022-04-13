import math

class TimeVaryingElastance:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
    
        # properties
        self.name = ""                        # name of the compliance
        self.type = "time_varying_elastance"  # type of the model component
        self.compound_names = []              # compounds of the model component.
        self.compound_concentrations = []
        self.is_enabled = True                # determines whether or not the compliance is enabled
        self.vol = 0                          # holds the volume in liters
        self.u_vol = 0                        # holds the unstressed volume in liters
        self.u_vol_fac = 1.0
        self.pres = 0                         # holds the net pressure in mmHg
        self.recoil_pressure = 0              # holds the recoil pressure in mmHg
        self.pres_outside = 0                 # holds the pressure which is exerted on the compliance from the outside
        self.pres_itp = 0                     # 
        self.pres_transmural = 0
        self.el_min = 1                       # holds the minimal elastance
        self.el_min_fac = 1.0
        self.el_max = 1                       # holds the maximal elastance
        self.el_max_fac = 1.0
        self.varying_elastance_factor = 0     # holds the varying elastance factor
        self.el_k = 0                         # holds the constant for the non-linear elastance function
        self.el_k_fac = 1.0
        self.compounds = {}                     # dictionary holding all the blood compounds
        self.initialized = False
    
        # set the independent properties (name, description, type, subtype, is_enabled, vol, u_vol, el_min, el_max, el_k)
        for key, value in args.items():
            setattr(self, key, value)
    
        # get a reference to the model
        self.model = model
        
        # systolic and diastolic pressures
        self.systole = 0
        self.diastole = 0
        self.mean = 0
        self.min_pres_temp = 0
        self.max_pres_temp = 0
        
        # systole and diastole window
        self.analysis_window = 1
        self.analysis_counter = 0
        
    def model_step(self):
         # during every model step the transmural pressure is calculates
        if (self.is_enabled):
            self.calculate_pressure()
    
    def calculate_pressure (self):

        # calculate the volume above the unstressed volume
        vol_above_unstressed = self.vol - self.u_vol
        
        if (vol_above_unstressed < 0):
            vol_above_unstressed = 0

        # calculate the elastance, which is volume dependent in a non-linear way and dependent on the varying elastance factor
        el_min = self.el_min * self.el_min_fac
        el_max = self.el_max * self.el_max_fac
        elastance = el_min + ((el_max - el_min) * self.varying_elastance_factor) + self.el_k * self.el_k_fac * pow(vol_above_unstressed, 2)
        
        # calculate the recoil pressure in the compliance due to the elastacity of the compliance
        self.recoil_pressure = (vol_above_unstressed * elastance) 

        # calculate the net pressure which refers to the pressure inside relative to the outside of a compartment.
        self.pres = self.recoil_pressure + self.pres_outside + self.pres_itp + self.p_atm
        
        self.pres_transmural = self.recoil_pressure + self.pres_outside - self.pres_itp + self.p_atm
        
        # reset the outside pressure as it needs to be set every model cycle
        self.pres_outside = 0
        
        # reset the intrathoracic pressure as it needs to be set every model cycle
        self.pres_itp = 0
        
        # determine min and max pressures
        if self.analysis_counter > self.analysis_window:
            self.systole = self.max_pres_temp
            self.max_pres_temp = -1000
            self.diastole = self.min_pres_temp
            self.min_pres_temp = 1000
            self.analysis_counter = 0
            self.mean = ((2 * self.diastole) + self.systole) / 3.0
        
        self.analysis_counter += self.model.modeling_stepsize
        
        if self.pres > self.max_pres_temp:
            self.max_pres_temp = self.pres
        
        if self.pres < self.min_pres_temp:
            self.min_pres_temp = self.pres

    def volume_in (self, dvol, comp_from):
        # this method is called when volume is added to this components
        if self.is_enabled:
            # add volume
            self.vol += dvol
            
        # check whether this compliance has a mix attribute.
        if (self.content == 'blood'):
            if (self.vol > 0):
                # calculate the change in compound concentration
                self.mix_blood(dvol, comp_from)

                # mix the non-fixed blood compounds if the volume is not zero
                for name, compound in self.compounds.items():
                    if not compound["fixed"]:
                        d_compound = (comp_from.compounds[name]["conc"] - compound["conc"]) * dvol
                        compound["conc"] = ((compound["conc"] * self.vol) + d_compound) / self.vol
            
        if (self.content == 'gas'):
            if (self.vol > 0):
                self.mix_gas(dvol, comp_from)
            
        # guard against negative volumes (will probably never occur in this routine)
        return self.protect_mass_balance

    def mix_blood(self, dvol, comp_from):
        # calculate the change in compound concentration
        d_o2 = (comp_from.to2 - self.to2) * dvol
        d_co2 = (comp_from.tco2 - self.tco2) * dvol
        self.to2 = ((self.to2 * self.vol) + d_o2) / self.vol
        self.tco2 = ((self.tco2 * self.vol) + d_co2) / self.vol
        
    def mix_gas(self, dvol, comp_from):
        # calculate the change in o2 concentration
        d_co2 = (comp_from.co2 - self.co2) * dvol
        self.co2 = ((self.co2 * self.vol) + d_co2) / self.vol
        
        # calculate the change in co2 concentration
        d_cco2 = (comp_from.cco2 - self.cco2) * dvol
        self.cco2 = ((self.cco2 * self.vol) + d_cco2) / self.vol
        
        # calculate the change in n2 concentration
        d_cn2 = (comp_from.cn2 - self.cn2) * dvol
        self.cn2 = ((self.cn2 * self.vol) + d_cn2) / self.vol
        
        # calculate the change in argon concentration
        d_cargon = (comp_from.cargon - self.cargon) * dvol
        self.cargon = ((self.cargon * self.vol) + d_cargon) / self.vol
        
    def volume_out (self, dvol, comp_from):
        if self.is_enabled:
          # change volume
          self.vol -= dvol

        # guard against negative volumes (will probably never occur in this routine)
        return self.protect_mass_balance
      
    def protect_mass_balance (self):
        if (self.vol < 0):
            # if there's a negative volume it might corrupt the mass balance of the model so we have to return the amount of volume which could not be displaced
            _nondisplaced_volume = -self.vol
            # set the current volume to zero
            self.vol = 0
            # return the amount volume which could not be removed
            return _nondisplaced_volume
        else:
            # massbalance is guaranteed
            return 0