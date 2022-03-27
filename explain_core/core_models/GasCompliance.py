import math

class GasCompliance:
    # this method is called when a new compliance is instantiated
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
    
        # properties
        self.name = ""                      # name of the compliance
        self.model_type = "GasCompliance"   # type of the model component
        self.content = "gas"                # content of the component (blood/gas/lymph)
        self.is_enabled = True              # determines whether or not the compliance is enabled
        self.vol = 0                        # holds the volume in liters
        self.u_vol = 0                      # holds the unstressed volume in liters
        self.u_vol_fac = 1.0                # holds the unstressed volume in liters multiplier
        self.pres = 0                       # holds the net pressure in mmHg
        self.recoil_pressure = 0            # holds the recoil pressure in mmHg
        self.pres_outside = 0               # holds the pressure which is exerted on the compliance from the outside
        self.pres_transmural = 0            # holds the transmural pressure off the compliance
        self.pres_rel = 0
        self.itp = 0                        # holds the intrathoracic pressure
        self.p_atm = 0
        self.el_base = 1.0                  # holds the baseline elastance
        self.el_base_fac = 1.0              # holds the baseline elastance multiplier
        self.el_k = 0                       # holds the constant for the non-linear elastance function
        self.el_k_fac = 1.0                 # holds the constant for the non-linear elastance function multiplier
    
        # set the values of the independent properties with the values from the JSON configuration file
        for key, value in args.items():
            setattr(self, key, value)

        # get a reference to the model to access other model components
        self.model = model

    # this method is called by the model engine in every model step
    def model_step (self):
        # during every model step the transmural pressure is calculates
        if (self.is_enabled):
            self.calculate_pressure()
        
    def calculate_pressure (self):
        # calculate the volume above the unstressed volume
        vol_above_unstressed = self.vol - self.u_vol * self.u_vol_fac

        # calculate the elastance, which is volume dependent in a non-linear way
        elastance = self.el_base * self.el_base_fac + self.el_k * self.el_k_fac * pow(vol_above_unstressed, 2)
        
        # calculate the recoil pressure in the compliance due to the elastacity of the compliance
        self.recoil_pressure = (vol_above_unstressed * elastance) 

        # calculate the net pressure which refers to the pressure inside relative to the outside of a compartment.
        self.pres = self.recoil_pressure + self.pres_outside + self.p_atm
        
        self.pres_rel = self.pres - self.p_atm
        
        # calculate the transmural pressure which refers to the difference between the recoil pressure and the pressure outside the compliance
        self.pres_transmural = self.recoil_pressure - self.pres_outside + self.p_atm
        
        # reset the outside pressure as it needs to be set every model cycle
        self.pres_outside = 0
        
        # we now have the new pressure and volume, let's calculate the gas composition
        # calculate the concentration of molecules in the gas object at the current pressure, volume and temperature using the gas law
        self.c_total = (self.pres / (self.gas_constant * (273.15 + self.temp))) * 1000
            
        # calculate the ph2o depending on the temperature
        self.ph2o = self.calculate_water_vapour_pressure(self.temp)
            
        # calculate the fh2o depending on the pressure
        self.fh2o = self.ph2o / self.pres
            
        # calculate the wet fractions from the fh2o and the dry fractions
        self.fo2 = self.fo2_dry * (1 - self.fh2o)
        self.fco2 = self.fco2_dry * (1 - self.fh2o)
        self.fn2 = self.fn2_dry * (1 - self.fh2o)
        self.fargon = self.fargon_dry * (1 - self.fh2o)
            
        # calculate the partial pressures
        self.po2 = self.fo2 * (1 - self.fh2o) * self.pres
        self.pco2 = self.fco2 * (1 - self.fh2o) * self.pres
        self.pn2 = self.fn2 * (1 - self.fh2o) * self.pres
        self.pargon = self.fargon * (1 - self.fh2o) * self.pres
            
        # calculate the concentrations
        self.co2 = self.fo2 * (1 - self.fh2o) * self.c_total
        self.cco2 = self.fco2 * (1 - self.fh2o) * self.c_total
        self.cn2 = self.fn2 * (1 - self.fh2o) * self.c_total
        self.cargon = self.fargon * (1 - self.fh2o) * self.c_total    
            

    def volume_in (self, dvol, comp_from):
        # this method is called when volume is added to this components
        if self.is_enabled and not self.fixed_composition:
            # add volume
            self.vol += dvol
 
        if (self.vol > 0 and not self.fixed_composition):
            dfo2_dry = (comp_from.fo2_dry - self.fo2_dry) * dvol
            self.fo2_dry = ((self.fo2_dry * self.vol) + dfo2_dry) / self.vol
        
            dfco2_dry = (comp_from.fco2_dry - self.fco2_dry) * dvol
            self.fco2_dry = ((self.fco2_dry * self.vol) + dfco2_dry) / self.vol
        
            dfn2_dry = (comp_from.fn2_dry - self.fn2_dry) * dvol
            self.fn2_dry = ((self.fn2_dry * self.vol) + dfn2_dry) / self.vol
        
            dfargon_dry = (comp_from.fargon_dry - self.fargon_dry) * dvol
            self.fargon_dry = ((self.fargon_dry * self.vol) + dfargon_dry) / self.vol
            
        # guard against negative volumes (will probably never occur in this routine)
        return self.protect_mass_balance

    def volume_out (self, dvol, comp_from):
        # this method is called when volume is removed from this components
        if self.is_enabled and not self.fixed_composition:
            # add volume
            self.vol -= dvol

        # guard against negative volumes (will probably never occur in this routine)
        return self.protect_mass_balance
        
    def exchange_gas(self, flux_o2, flux_co2):
        # flux unit is in mmol so have to find a way to substract or add this to the gas and then we have to calculate back to the fo2_dry!
        
        # calculate the wet fo2
        self.fo2 = self.fo2_dry * (1 - self.fh2o)
        self.fco2 = self.fco2_dry * (1 - self.fh2o)
        
        # convert the wet fo2 to mmol O2, add the flux O2 and convert back to fo2
        new_fo2 = (((self.fo2 * self.c_total * self.vol) + flux_o2) / self.vol) / self.c_total
        new_fco2 = (((self.fco2 * self.c_total * self.vol) + flux_co2) / self.vol) / self.c_total

        # calculate back to the dry fo2
        self.fo2_dry = new_fo2 / (1 - self.fh2o)
        self.fco2_dry = new_fco2 / (1 - self.fh2o)

    def protect_mass_balance (self):
        if (self.vol < 0):
            # if there's a negative volume it might corrupt the mass balance of the model so we have to return the amount of volume which could not be displaced to the caller of this function
            _nondisplaced_volume = -self.vol
            # set the current volume to zero
            self.vol = 0
            # return the amount volume which could not be removed
            return _nondisplaced_volume
        else:
            # massbalance is guaranteed
            return 0
        
    def calculate_water_vapour_pressure(self, temp):
        # calculate the water vapour pressure in air depending on the temperature
        return math.pow(math.e, (20.386 - (5132 / (temp + 273)))) 