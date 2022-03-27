import math

class Ans:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        #
        self.d_map_hp = 0;
        self.d_map_cont = 0;
        self.d_map_venpool = 0;
        self.d_map_res = 0;

        self.d_lungvol_hp = 0;
        self.d_po2_hp = 0;
        self.d_pco2_hp = 0;

        self.d_po2_ve = 0;
        self.d_pco2_ve = 0;
        self.d_ph_ve = 0;

        self.a_map = 0;
        self.a_lungvol = 0;
        self.a_po2 = 0;
        self.a_pco2 = 0;
        self.a_ph = 0;

        self._update_timer = 0;
        self.ans_update_interval = 0.015;
        
        self.input_hp = ['AA']
        self.input_ve = ['AA']
        self.input_cont = ['AA']
        self.input_venpool = ['AA']
        self.input_res = ['AA']
        
        self.targets_hp = ['ecg']
        self.targets_ve = ['breathing']
        self.targets_cont = ['LV','RV']
        self.targets_venpool = ['IVCE','SVC']
        self.targets_res = ['AD_RLB','AD_KID','AD_INT','AD_LS']
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the whole model
        self.model = model
        
        # define the update counters as the ANS doesn't need to be updated every 0.5 ms
        self.update_counter = 0
        self.update_interval = 0.005
        
        # set the init flag to false
        self.initialized = False
        
        
        self.ref_uvol_ivce = 0
        self.ref_uvol_svc = 0

        self.delta_vol = 0
        self.prev_delta_vol = 0
        
    def model_step(self):
        if self.is_enabled:
            if (self.update_counter > self.update_interval):
                self.update_counter = 0
                self.ans_activity()
                
            self.update_counter += self.model.modeling_stepsize
    
    def initialize(self):
        # switch on the acidbase and oxygenation capabilities of the inputs
        for comp in self.input_hp:
            self.model.components[comp].oxy_enabled = True
            self.model.components[comp].acidbase_enabled = True
        
        self.ref_uvol_ivce = self.model.components["IVCE"].u_vol
        
        # set the initialization flag to true
        self.initialized = True
        
    def ans_activity(self):
        # check whether or not the model is initialized
        if not self.initialized:
            self.initialize()
            
        # activate the inputs
        self.model.components['AA'].oxy_enabled = True
        self.model.components['AA'].acidbase_enabled = True
        
        # calculate the activation functions
        self.a_map = self.activation_function(self.model.components["AA"].pres, self.sa_map, self.op_map, self.th_map)
        self.a_po2 = self.activation_function(self.model.components["AA"].po2, self.sa_po2, self.op_po2, self.th_po2)
        self.a_pco2 = self.activation_function(self.model.components["AA"].pco2, self.sa_pco2, self.op_pco2, self.th_pco2)
        self.a_ph = self.activation_function(self.model.components["AA"].ph, self.sa_ph, self.op_ph, self.th_ph)
        
        # calculate the effectors
        self.d_map_hp = self.update_interval * ((1 / self.tc_map_hp) * (-self.d_map_hp + self.a_map)) + self.d_map_hp
        self.d_po2_hp = self.update_interval * ((1 / self.tc_po2_hp) * (-self.d_po2_hp + self.a_po2)) + self.d_po2_hp
        self.d_pco2_hp = self.update_interval * ((1 / self.tc_pco2_hp) * (-self.d_pco2_hp + self.a_pco2)) + self.d_pco2_hp
        
        self.d_po2_ve = self.update_interval * ((1 / self.tc_po2_ve) * (-self.d_po2_ve + self.a_po2)) + self.d_po2_ve
        self.d_pco2_ve = self.update_interval * ((1 / self.tc_pco2_ve) * (-self.d_pco2_ve + self.a_pco2)) + self.d_pco2_ve
        self.d_ph_ve = self.update_interval * ((1 / self.tc_ph_ve) * (-self.d_ph_ve + self.a_ph)) + self.d_ph_ve
        
        self.d_map_cont = self.update_interval * ((1 / self.tc_map_cont) * (-self.d_map_cont + self.a_map)) + self.d_map_cont
        self.d_map_venpool = self.update_interval * ((1 / self.tc_map_venpool) * (-self.d_map_venpool + self.a_map)) + self.d_map_venpool
        self.d_map_res = self.update_interval * ((1 / self.tc_map_res) * (-self.d_map_res + self.a_map)) + self.d_map_res
        
        # apply the effects
        
        # if blood pressure above operating point the self.d_map_hp is positive and self.g_map_hp is positive
        heartrate_ref = self.model.components['ecg'].heart_rate_ref
        new_heartrate = 60000.0 / (60000.0 / heartrate_ref + self.g_map_hp * self.d_map_hp + self.g_pco2_hp * self.d_pco2_hp + self.g_po2_hp * self.d_po2_hp)
        if new_heartrate < 0:
            new_heartrate = 0
        self.model.components['ecg'].heart_rate = new_heartrate
        
        mv_ref = self.model.components['breathing'].ref_minute_volume
        new_mv = mv_ref + self.g_ph_ve * self.d_ph_ve + self.g_pco2_ve * self.d_pco2_ve + self.g_po2_ve * self.d_po2_ve;
        if new_mv < 0:
            new_mv = 0
        self.model.components['breathing'].target_minute_volume = new_mv
        
        self.delta_vol = self.g_map_venpool * self.d_map_venpool
        self.model.components['IVCE'].u_vol = self.ref_uvol_ivce + self.delta_vol
        
        # to conserve the mass balance we have to change the volume of the IVCE according to delta_vol
        self.model.components['IVCE'].vol -= (self.delta_vol - self.prev_delta_vol)
        self.prev_delta_vol = self.delta_vol
        
    def activation_function(self, value, saturation, operating_point, threshold):
        activation = 0;

        if value >= saturation:
            activation = saturation - operating_point
        else:
            if value <= threshold:
                activation = threshold - operating_point
            else:
                activation = value - operating_point

        return activation
