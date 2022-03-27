import math

class Metabolism:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # define the properties
        self.name = "metabolism"
        self.description = "metabolism"
        self.model_type = "Metabolism"
        self.is_enabled = True
        self.atp_need = 0.00014
        self.resp_q = 0.8
        self.p_atm = 760
        self.outside_temp = 20
        self.body_temp = 36.9
        self.active_comps = [
            {  "comp": "RLB", "fvatp": 0.185 },
            {  "comp": "KID", "fvatp": 0.1 },
            {  "comp": "LS", "fvatp": 0.1 },
            {  "comp": "INT", "fvatp": 0.1 },
            {  "comp": "RUB", "fvatp": 0.2 },
            {  "comp": "BR", "fvatp": 0.25 },
            {  "comp": "COR", "fvatp": 0.05 },
            {  "comp": "AA", "fvatp": 0.005 },
            {  "comp": "AD", "fvatp": 0.01 }
         ]

        # fill the properties with the values from the JSON configuration file
        for key, value in args.items():
            setattr(self, key, value)
        
        # get a reference to the model
        self.model = model
  
    def model_step(self):
        if self.is_enabled:
            for active_comp in self.active_comps:
                self.calculate_energy_use(active_comp)
    
    def calculate_energy_use(self, active_comp):
        # store a reference to the component
        comp = self.model.components[active_comp["comp"]]
        
        # find the stored fractional atp use
        fvatp = active_comp["fvatp"]
        
        # get the component ATP need in molecules per second
        atp_need = fvatp * self.atp_need
        
        # now we need to know how much molecules ATP we need in this step
        atp_need_step = atp_need * self.model.modeling_stepsize
        
        # get the number of oxygen molecules available in this active compartment in mmol
        o2_molecules_available = comp.to2 * comp.vol
        
        # we state that 80% of these molecules are available for use
        o2_molecules_available_for_use = 0.8 * o2_molecules_available
        
        # how many molecules o2 do we need to burn in this step as 1 mmol of o2 gives 5 mmol of ATP when processed by oxydative phosphorylation
        o2_to_burn = atp_need_step / 5.0
        
        # how many needed ATP molecules can't be produced by aerobic respiration
        anaerobic_atp = (o2_to_burn - o2_molecules_available_for_use / 4.0) * 5.0
        
        # if negative then there are more o2 molecules available than needed and then shut down anaerobic fermentation
        if (anaerobic_atp < 0):
            anaerobic_atp = 0
        
        # burn the required amount of o2 molecules
        o2_burned = o2_to_burn
        
        # if we need to burn more than we have then burn all available o2 molecules
        if (o2_to_burn > o2_molecules_available_for_use):
            # burn all o2's
            o2_burned = o2_molecules_available_for_use
            
        # as we burn o2 molecules we have to substract them from the total number of o2 molecules
        o2_molecules_available -= o2_burned
        
        # calculate the new tO2
        comp.to2 = o2_molecules_available / comp.vol
        
        # guard against negative concentrations
        if comp.to2 < 0:
            comp.to2 = 0
            
        # we now how much o2 molecules we'v burned so we should be able to calculate how much co2 molecules we generated. This depends on the respiratory quotient
        co2_molecules_produced = o2_burned * self.resp_q
        
        # add the co2 molecules to the total co2 molecules
        comp.tco2 = ((comp.tco2 * comp.vol) + co2_molecules_produced) / comp.vol
        
        # guard against negative concentrations
        if comp.tco2 < 0:
            comp.tco2 = 0
        
        
