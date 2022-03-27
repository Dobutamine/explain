import math

class Gas:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        

        # define dictionaries for the independent variables
        self.temp_settings = {}
        self.dry_air_composition = {}
        self.gas_compounds = {}
        
        # set the independent properties with the values as defined in the JSON model_definition file
        for key, value in args.items():
              setattr(self, key, value)
        
        # get a reference to the whole model
        self.model = model
        
        # now transform the components with content gas into gas components
        for comp_name, comp in model.components.items():
            if hasattr(comp, 'content'):
                if (comp.content == 'gas'):
#                     print(comp.name)
                    # now transform the model component into a gas containing object by injecting the necessary methods and properties
                    setattr(comp, 'p_atm', self.p_atm)      # sets the p_atm independent variable as property of the gas object
                    setattr(comp, 'c_total', 0)             # sets the c_total dependent variable as property of the gas object
                    setattr(comp, 'c_total_dry', 0)         # sets the c_total_dry dependent variable as property of the gas object
                    
                    # set the temperature and the water vapour pressure which is temperature dependent as properties of the gas object
                    for temp in self.temp_settings:
                        if temp == comp.name:
                            setattr(comp, "gas_constant", self.gas_constant)
                            setattr(comp, "temp", self.temp_settings[temp])
                            setattr(comp, "ph2o", self.calculate_water_vapour_pressure(self.temp_settings[temp]))
                    
                    # calculate concentration of all gas molecules in the gas compartment at atmospheric pressure
                    comp.c_total = (self.p_atm / (comp.gas_constant * (273.15 + comp.temp))) * 1000
                    
                    # calculate the fraction of h2o
                    setattr(comp, 'fh2o', comp.ph2o / self.p_atm)
                    setattr(comp, 'ch2o', comp.fh2o * comp.c_total)
                    
                    # we can now calculate the h2o corrected fractions of the other gasses as the total of fractions should 1.0

                    # initialize the gas object with the wet air composition fractions (as a starting condition)
                    for compound, value in self.dry_gas_fractions.items():
                        # set the fraction
                        setattr(comp, "f" + compound, value * (1.0 - comp.fh2o))
                        # print(f'f{compound} = {value * (1.0 - comp.fh2o)}')
                                        
                        # calculate the concentration of the compound in the dry part of the gas
                        setattr(comp, "c" + compound, value * (1.0 - comp.fh2o) * comp.c_total)
                                        
                        # calculate the partial pressure of the gas compound
                        setattr(comp, "p" + compound, value * (1.0 - comp.fh2o) * self.p_atm )
                        
                    sum_f_wet = comp.fh2o + comp.fo2 + comp.fco2 + comp.fn2 + comp.fargon
                    sum_c_wet = comp.ch2o + comp.co2 + comp.cco2 + comp.cn2 + comp.cargon  
                    
                    # dry air part
                    # comp.c_total_dry = comp.c_total - comp.ch2o
                    comp.c_total_dry = (self.p_atm / (comp.gas_constant * (273.15 + comp.temp))) * 1000
                    
                    for compound, value in self.dry_gas_fractions.items():
                        # set the fraction
                        setattr(comp, "f" + compound + "_dry", value)
                        # print(f'f{compound}_dry = {value}')
                                        
                        # calculate the concentration of the compound in the dry part of the gas
                        setattr(comp, "c" + compound + "_dry", value * comp.c_total_dry)
                                        
                        # calculate the partial pressure of the gas compound
                        setattr(comp, "p" + compound + "_dry", value * self.p_atm )
                    
                    sum_f_dry = comp.fo2_dry + comp.fco2_dry + comp.fn2_dry + comp.fargon_dry
                    sum_c_dry = comp.co2_dry + comp.cco2_dry + comp.cn2_dry + comp.cargon_dry
                    
    def model_step(self):
        pass

    def calculate_water_vapour_pressure(self, temp):
        # calculate the water vapour pressure in air depending on the temperature
        return math.pow(math.e, (20.386 - (5132 / (temp + 273)))) 
        
