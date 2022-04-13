import math

class Ans:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
            
        # get a reference to the whole model
        self.model = model
        
        # define the update counters as the ANS doesn't need to be updated every 0.5 ms
        self.update_counter = 0
        self.update_interval = 0.005
        
        # set the init flag to false
        self.initialized = False

        # define a pathway list
        self.pathways = []
        self.ans_pathways = {}

        # define a effector site dictionary
        self.effector_sites = []
        self.ans_effector_sites = {}

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
    def model_step(self):
        if self.is_enabled:
            if (self.update_counter > self.update_interval):
                self.update_counter = 0
                self.ans_activity()
                
            self.update_counter += self.model.modeling_stepsize
    
    def initialize(self):
        # analyze the different effector sites and pathways and setup the model structure
        for effector_site in self.effector_sites:
            # instantiate an effector site
            new_effector_site = EffectorSite(self.model, effector_site)

            # add the new effector site to the effector dictionary
            self.ans_effector_sites[new_effector_site.name] = new_effector_site

        for pathway in self.pathways:
            # instantiate a pathway
            new_pathway = Pathway(self.model, self.update_interval, pathway)

            # add the new pathway to the pathways dictionary
            self.ans_pathways[new_pathway.name] = new_pathway

        # set the initialization flag to true
        self.initialized = True

    def ans_activity(self):
        # only initialize the ANS AFTER everything else
        if not self.initialized:
            self.initialize()

        # first calculate all pathways and set the effector
        for (_, pathway) in self.ans_pathways.items():
            # get the effector site and the effector
            (effector_site, effect) = pathway.calculate_pathway()

            # update the cummulative effector on the effector site
            self.ans_effector_sites[effector_site].effect_cum += effect

        # apply the effects and reset the cummulative effector
        for (_, effector_site) in self.ans_effector_sites.items():
            # update the effector
            effector_site.update_effector()


class EffectorSite:
    def __init__(self, model, effector_args):
        super().__init__()

        self.model = model

        # initialize the effector site
        effector = effector_args["effector"].split(".")
        self.effector_model = model.components[effector[0]]
        self.effector_prop = effector[1]
        self.effector_reference = effector_args["reference"]
        
        self.name = effector_args["name"]
        self.is_enabled = effector_args["is_enabled"]

        # define state variables
        self.effect_cum = 0
        self.prev_delta_vol = 0
    
    def update_effector(self):
        

        # conserve the mass
        if (self.effector_prop == "u_vol"):
            # calculated the new unstressed volume
            new_unstressed_volume = self.effector_reference  + self.effect_cum

            # set the new unstressed volume
            setattr(self.effector_model, self.effector_prop, new_unstressed_volume)

            # get current volume
            current_vol_value = getattr(self.effector_model, "vol")
            
            # calculate the relative volume change of this step
            vol_change = self.effect_cum - self.prev_delta_vol
            
            # set the new volume
            setattr(self.effector_model, "vol", current_vol_value - vol_change)

            # store the previous volume change
            self.prev_delta_vol = self.effect_cum
        else:
            # calculate the new value
            new_value = self.effector_reference  + self.effect_cum

            # apply the new value
            setattr(self.effector_model, self.effector_prop, new_value)

        # reset the
        self.effect_cum = 0



class Pathway:
    def __init__(self, model, update_interval, pathway_args):
        # initialize the super class
        super().__init__()

        self.model = model
        self.update_interval = update_interval

        # initialize the pathway
        input = pathway_args["input"].split(".")
        self.input_model = model.components[input[0]]
        self.input_prop = input[1]

        # check whether the input model needs to activate the oxygenation and acidbase model
        if (self.input_prop == "po2" or self.input_prop == "pco2" or self.input_prop == "ph"):
            self.input_model.oxy_enabled = True
            self.input_model.acidbase_enabled = True

        self.name = pathway_args["name"]
        self.is_enabled = pathway_args["is_enabled"]
        self.gain = pathway_args["gain"]
        self.time_constant = pathway_args["time_constant"]

        # define activation and effector variables 
        self.d = 0
        self.net_effect = 0
        self.threshold = pathway_args["threshold"]
        self.operating_point = pathway_args["operating_point"]
        self.saturation = pathway_args["saturation"]
        self.time_constant = pathway_args["time_constant"]
        self.gain = pathway_args["gain"]
        self.effector_site = pathway_args["effector_site"]

        # define the state variables
        self.input_value = 0
        self.effector_value = 0

    
    def calculate_pathway(self):
        # get value
        value = getattr(self.input_model, self.input_prop)

        # calculate the activation function
        activation= self.activation_function(value)
        
        # caluclate the effector value
        self.d = self.effector_function(activation)
        
        # apply the effect
        self.net_effect = self.d * self.gain

        return (self.effector_site, self.net_effect)



    def effector_function(self, activation):
        return self.update_interval * ((1 / self.time_constant) * (-self.d + activation)) + self.d

    def activation_function(self, value):
        activation = 0

        if value >= self.saturation:
            activation = self.saturation - self.operating_point
        else:
            if value <= self.threshold:
                activation = self.threshold - self.operating_point
            else:
                activation = value - self.operating_point

        return activation

    


        # apply the effects
        
        # if blood pressure above operating point the self.d_map_hp is positive and self.g_map_hp is positive
        # heartrate_ref = self.model.components['ecg'].heart_rate_ref
        # new_heartrate = 60000.0 / (60000.0 / heartrate_ref + self.g_map_hp * self.d_map_hp + self.g_pco2_hp * self.d_pco2_hp + self.g_po2_hp * self.d_po2_hp)
        # if new_heartrate < 0:
        #     new_heartrate = 0
        # self.model.components['ecg'].heart_rate = new_heartrate
        
        # mv_ref = self.model.components['breathing'].ref_minute_volume
        # new_mv = mv_ref + self.g_ph_ve * self.d_ph_ve + self.g_pco2_ve * self.d_pco2_ve + self.g_po2_ve * self.d_po2_ve;
        # if new_mv < 0:
        #     new_mv = 0
        # self.model.components['breathing'].target_minute_volume = new_mv
        
        # self.delta_vol = self.g_map_venpool * self.d_map_venpool
        # self.model.components['IVCE'].u_vol = self.ref_uvol_ivce + self.delta_vol
        
        # # to conserve the mass balance we have to change the volume of the IVCE according to delta_vol
        # self.model.components['IVCE'].vol -= (self.delta_vol - self.prev_delta_vol)
        # self.prev_delta_vol = self.delta_vol

