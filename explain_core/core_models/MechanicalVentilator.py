import math

class MechanicalVentilator:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # independent properties (later set by JSON file settings)
        self.p_atm = 760
        
        # Ventilator modes
        # 0 = Pressure Control (PC), 1 = Volume Control, 2 = Pressure Regulated Volume Control (PRVC), 3 = HFOV
        self.ventilator_mode = 0
        
        self.cycling_mode = 0
        self.t_in = 0.4
        self.t_ex = 1.0
        self.freq = 42
        self.inspiratory_flow = 8
        self.expiratory_flow = 2
        self.bias_flow = 8
        self.max_pip = 20
        self.pip = 20
        self.peep = 5
        self.target_tidal_volume = 0.0165
        self.fio2 = 0.21
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the whole model
        self.model = model
        
        # get a reference to the modeling stepsize
        self.t = self.model.modeling_stepsize

        # declare the state variables
        self.inspiration = True
        self.inspiration_counter = 0
        self.expiration = False
        self.expiration_counter = 0
        self.inspiratory_tidal_volume_counter = 0
        self.inspiratory_tidal_volume = 0
        self.expiratory_tidal_volume_counter = 0
        self.expiratory_tidal_volume = 0
        self.measured_freq_counter = 0
        self.measured_freq_temp = 0
        self.measured_freq = 0
        self.exhaled_minute_volume = 0
        self.peak_pressure_temp = - 1000

        # sensors
        self.sensor_insp_flow = 0
        self.sensor_flow = 0
        self.sensor_volume = 0
        self.sensor_pressure = 0
        self.sensor_co2 = 0
        self.sensor_etco2 = 0
        
        # pressure control
        self.pc_pip_reached = False
        self.pc_peep_reached = False
        
        self.error = 0
        self.kp = 500
        self.error_int = 0
        self.ki = 0
        self.error_dif = 0
        self.kd = 5
        self.prev_sensor_value = 0
        
        self.error_out = 0 
        self.error_int_out = 0
        self.error_dif_out = 0
        
        # prvc
        self.prvc_tv_range = 5
        self.prvc_pres_adjusted = False
        
        # hfov sinus
        self.hfov_pres = 0
        self.hfov_counter = 0
        
    def model_step(self):
        if self.is_enabled:
            self.model_cycle()
            
    def model_cycle(self):
        # get the model stepsize
        self.t = self.model.modeling_stepsize
        
        # get a reference to the in- and expiration valves
        self.insp_valve = self.model.components['VENT_INSP_VALVE']
        self.exp_valve = self.model.components['VENT_EXP_VALVE']

        # get the ventilator sensory inputs
        flow = self.model.components['YPIECE_NCA'].flow * 60.0
        if (flow > 0):
            self.sensor_insp_flow = flow
        
        self.sensor_flow = flow
        self.sensor_pressure = (self.model.components['YPIECE'].pres) - self.p_atm    # in mmHg
        self.sensor_volume += self.model.components["YPIECE_NCA"].flow * self.t     # in l
        self.sensor_co2 = self.model.components["NCA"].pco2
        
        # ventilator mode
        if self.ventilator_mode == 0:
            self.pressure_control()
        elif self.ventilator_mode == 1:
            self.volume_control()
        elif self.ventilator_mode == 2:
            self.pressure_regulated_volume_control()
        elif self.ventilator_mode == 3:
            self.hfov()
        else:
            self.pressure_control()
            
        # check whether there's an inspiration
        if (self.inspiration): 
            # increase the inspiratory tidal volume counter
            self.inspiratory_tidal_volume_counter += self.model.components['VENT_INSP_VALVE'].flow * self.t
            
            # find the peak pressure
            if self.sensor_pressure > self.peak_pressure_temp:
                self.peak_pressure_temp = self.sensor_pressure
            
            # increase the inspiration timer
            self.inspiration_counter += self.t
        
        #check whether there's an expiration
        if (self.expiration):
            # increase the exhaled tidal volume
            self.expiratory_tidal_volume_counter += self.model.components['VENT_EXP_VALVE'].flow * self.t
            
            # increase the expiration timer
            self.expiration_counter += self.t
        
        # determine the ventilator frequency, needed for triggered ventilator modes
        self.measured_freq_counter += self.t
        self.measured_freq_temp = 60 / self.measured_freq_counter
        
        # cycle the inspiration and expiration of the ventilator
        self.ventilator_cycling()
    
    def hfov(self):
        # apply the MAP by setting
        
        # open the expiration valve and set the mean airway pressure
        self.exp_valve.no_flow = False
        # open the valve and set the mean airway pressure
        self.exp_valve.r_for = 10
        self.model.components['VENTOUT'].vol = (self.peep / self.model.components['VENTOUT'].el_base) + self.model.components['VENTOUT'].u_vol
        
        # apply the bias flow, open the inspiratory flow
        self.insp_valve.no_flow = False
        self.insp_valve.r_for = (self.model.components['VENTIN'].pres - self.model.components['VENTOUT'].pres) / (self.inspiratory_flow / 60)
        
        # add additional pressure to the YPIECE
        # apply the sinusoid inspiration
        signal = math.sin(self.hfov_counter) * 25
        # so each step = 0.0005 s
        # 10 herz is 10 sinosoid per second so 2 * pi is one period 
        stepsize = 10 * (2 * math.pi) * self.model.modeling_stepsize
        self.hfov_counter += stepsize
        if self.hfov_counter > 2 * math.pi:
            self.hfov_counter = 0
        self.model.components['YPIECE'].pres_outside = signal
        
        
                    
    
    def volume_control (self):
        if self.inspiration:
            self.pc_peep_reached = False
            
            # close the expiratory valve
            self.exp_valve.no_flow = True
            
            # open the inspiratory valve
            self.insp_valve.no_flow = False
            
            # track the inspiratory volume and until then keep the flow constant
            if self.inspiratory_tidal_volume_counter > self.target_tidal_volume:
                self.insp_valve.no_flow = True
                
            if self.sensor_pressure > self.max_pip:
                self.insp_valve.no_flow = True
            
            self.regulate_inspiratory_flow()
                
        
        if self.expiration:
            # close the inspiration valve
            self.insp_valve.no_flow = True
            
            # open the expiration valve
            self.exp_valve.no_flow = False
            
            # open the expiration valve
            if self.sensor_pressure <= self.peep and not self.pc_peep_reached:
                self.pc_peep_reached = True
                self.reset_regulator_peep()
                
            if self.pc_peep_reached:
                self.insp_valve.no_flow = True
                self.regulate_pressure_peep(self.peep)
            else:
                self.exp_valve.r_for = 20
            
    def pressure_regulated_volume_control(self):
        if self.inspiration and not self.prvc_pres_adjusted:
            self.prvc_pres_adjusted = True
            # check whether the tidal volume was reached or not
            if self.expiratory_tidal_volume < (self.target_tidal_volume - (self.target_tidal_volume * self.prvc_tv_range / 100)):
                # tidal volume is below the target so increase the pip
                self.pip += 1
                if self.pip > self.max_pip:
                    self.pip = self.max_pip
            if self.expiratory_tidal_volume > (self.target_tidal_volume + (self.target_tidal_volume * self.prvc_tv_range / 100)):
                # tidal volume is below the target so decrease the pip
                self.pip -= 1
                if self.pip - self.peep < 2:
                    self.pip = self.peep + 2
        
        if self.expiration:
            self.prvc_pres_adjusted = False
        
        # do a pressure control
        self.pressure_control()
        
    def pressure_control(self):

        if self.inspiration:
            # reset the peep flag
            self.pc_peep_reached = False
            
            # close the expiration valve
            self.exp_valve.no_flow = True
            
            # open the inspiration valve and set the driving pressure
            self.insp_valve.no_flow = False
            self.model.components['VENTIN'].vol = (2500 / self.model.components['VENTIN'].el_base) + self.model.components['VENTIN'].u_vol
            
            # check whether the pip has been reached
            if self.sensor_pressure >= self.pip and not self.pc_pip_reached:
                # signal that the pressure limiter should switch on
                self.pc_pip_reached = True
                # reset the pressure limiter
                self.reset_pressure_limiter()
            
            # if pip is reached then the pressure limiter kicks in
            if self.pc_pip_reached:
                # limit the pressure by changing the resistance of the inspiratory valve
                self.pressure_limiter(self.pip, self.insp_valve, 5)
            else:
                # calculate the inspiratory flow
                self.insp_valve.r_for = (self.model.components['VENTIN'].pres - self.model.components['VENTOUT'].pres) / (self.inspiratory_flow / 60)
                
        if self.expiration:
            # reset the pip flag
            self.pc_pip_reached = False
            
            # close the inspiration valve
            self.insp_valve.no_flow = True
            
            # open the expiration valve and set the peep
            self.exp_valve.no_flow = False
            self.exp_valve.r_for = 10
            
            self.model.components['VENTOUT'].vol = (self.peep / self.model.components['VENTOUT'].el_base) + self.model.components['VENTOUT'].u_vol
            
#             # check whether the peep has been reached
#             if (self.sensor_pressure <= self.peep):
#                 self.pc_peep_reached = True
#                 self.model.components['VENTOUT'].vol = (self.peep / self.model.components['VENTOUT'].el_base) + self.model.components['VENTOUT'].u_vol
    
    def reset_pressure_limiter(self):
        # reset the previous value
        self.prev_sensor_value = self.sensor_pressure
        
        # reset the integrator
        self.error_int = 0
        self.error = 0
    
    def pressure_limiter(self, target_pressure, target, lower_limit = 5, upper_limit = -1):
        # error calculator
        self.error = self.sensor_pressure - target_pressure
        
        # integrator
        self.error_int += self.error * self.t
        
        # differentiator
        self.error_dif = (self.prev_sensor_value - self.sensor_pressure) / self.t
        
        # store previous value
        self.prev_sensor_value = self.sensor_pressure
        
        # calculate the output
        output = (self.error * self.kp) + (self.error_int * self.ki) - (self.error_dif * self.kd)
        
        self.error_out = (self.error * self.kp)
        self.error_int_out = (self.error_int * self.ki)
        self.error_dif_out = (self.error_dif * self.kd)
        
        # apply the output
        target.r_for += output
        
        if  target.r_for < lower_limit:
            target.r_for = lower_limit
        
        if target.r_for > upper_limit and upper_limit > 0:
            target.r_for = upper_limit
    
    def reset_peep_valve(self):
        # reset the previous value
        self.prev_sensor_value_peep = self.sensor_pressure
        
        # reset the integrator
        self.error_int_peep = 0
        
    def peep_valve(self):
        self.model.components['VENTOUT'].vol = (self.peep / self.model.components['VENTOUT'].el_base) + self.model.components['VENTOUT'].u_vol
        
        # error calculator
        self.error_peep = self.sensor_pressure - self.peep
        
        # integrator
        self.error_int_peep += self.error_peep * self.t
        
        # differentiator
        self.error_dif_peep = (self.prev_sensor_value_peep - self.sensor_pressure) / self.t
        
        # store the previous value
        self.prev_sensor_value_peep = self.sensor_pressure
        
        # calculate the output
        output = (self.error_peep * self.kp_peep) + (self.error_int_peep * self.ki_peep) - (self.error_dif_peep * self.kd_peep)
        
         # apply the output
        self.exp_valve.r_for += output
        
        if self.exp_valve.r_for < 5:
            self.exp_valve.r_for = 5
            
        self.exp_valve.r_for = 5
        
        
    def ventilator_cycling(self):
        if (self.cycling_mode == 0):
            self.time_cycling()
    
    def time_cycling(self):
        # determine the expiration time
        self.t_ex = (60.0 / self.freq) - self.t_in
        
        # check the cycling times
        if self.inspiration_counter > self.t_in:
            self.begin_expiration()
        
        if self.expiration_counter > self.t_ex:
            self.begin_inspiration()            
            
    def begin_inspiration(self):
        # determine the ventilator frequency
        self.measured_freq = 60 / self.measured_freq_counter
        
        # determine the expiratory tidal volume and minute volume
        self.expiratory_tidal_volume = self.expiratory_tidal_volume_counter
        self.exhaled_minute_volume = self.measured_freq * self.expiratory_tidal_volume
        
        # determine the end-tidal co2
        self.sensor_etco2 = self.model.components['NCA'].pco2
        
        # reset the counters
        self.expiration_counter = 0
        self.measured_freq_counter = 0
        self.expiratory_tidal_volume_counter = 0
        self.sensor_volume = 0;
        
        # set the states
        self.expiration = False
        self.inspiration = True

        
    def begin_expiration(self):
   
        # determine the peak pressure of the inspiration
        self.peak_pressure = self.peak_pressure_temp
        
        # determine the inspiratory tidal volume
        self.inspiratory_tidal_volume = self.inspiratory_tidal_volume_counter
        
        # reset the counters
        self.peak_pressure_temp = -100
        self.inspiratory_tidal_volume_counter = 0  
        self.inspiration_counter = 0
        
        # set the states
        self.expiration = True
        self.inspiration = False
    
    def toggle_ventilator(self, state):
        # toggle the ventilator
        self.model.components['ventilator'].is_enabled = state
        
        # ventilator compartments
        self.model.components['YPIECE'].is_enabled = state
        self.model.components['VENTIN'].is_enabled = state
        self.model.components['TUBINGIN'].is_enabled = state
        self.model.components['TUBINGOUT'].is_enabled = state
        self.model.components['VENTOUT'].is_enabled = state
            
        # ventilator valves
        self.model.components['VENT_INSP_VALVE'].is_enabled = state
        self.model.components['VENT_INSP_VALVE'].no_flow = not state
        
        self.model.components['TUBINGIN_YPIECE'].is_enabled = state
        self.model.components['TUBINGIN_YPIECE'].no_flow = not state
        
        self.model.components['YPIECE_TUBINGOUT'].is_enabled = state
        self.model.components['YPIECE_TUBINGOUT'].no_flow = not state
        
        self.model.components['TUBINGIN_TUBINGOUT'].is_enabled = state
        self.model.components['TUBINGIN_TUBINGOUT'].no_flow = not state
        
        self.model.components['VENT_EXP_VALVE'].is_enabled = state
        self.model.components['VENT_EXP_VALVE'].no_flow = not state
        
        # tubing connection
        self.model.components['YPIECE_NCA'].is_enabled = state
        self.model.components['YPIECE_NCA'].no_flow = not state
    
        # toggle spontaneous breathing
        self.model.components['OUT_NCA'].is_enabled = not state
        self.model.components['OUT_NCA'].no_flow = state
        self.model.components['breathing'].is_enabled = not state
    
    def set_ventilator_settings(self, mode="pc", freq=30, tidal=16, insp_time=0.4, insp_flow=8, max_pip=20, peep=5, fio2=0.21):
        self.freq = freq
        self.target_tidal_volume = tidal / 1000.0
        self.max_pip = max_pip 
        self.pip = max_pip 
        self.t_in = insp_time
        self.peep = peep 
        self.inspiratory_flow = insp_flow
        if fio2 > 10:
            fio2 = fio2 / 100
        
        if fio2 > 1:
            fio2 = 1
        if fio2 < 0.21:
            fio2 = 0.21
            
        self.fio2 = fio2
        
        if mode == "pc":
            self.ventilator_mode = 0
        elif mode == "vc":
            self.ventilator_mode = 1
        elif mode == "prvc":
            self.ventilator_mode = 2
        elif mode == "hfov":
            self.ventilator_mode = 3
        else:
            self.ventilator_mode = 0
            
        self.toggle_ventilator(True)

    def get_ventilator_settings(self):
        vent_settings = {}
        vent_settings['freq'] = self.freq
        vent_settings['target_tidal_volume'] = self.target_tidal_volume * 1000
        vent_settings['max_pip'] = self.max_pip 
        vent_settings['pip'] = self.pip 
        vent_settings['peep'] = self.peep 
        vent_settings['fio2'] = self.fio2
        vent_settings['insp_time'] = self.t_in
        vent_settings['insp_flow'] = self.inspiratory_flow
        
        if self.ventilator_mode == 0:
            vent_settings['mode'] = "pc"
        elif self.ventilator_mode == 1:
            vent_settings['mode'] = "vc"
        elif self.ventilator_mode == 2:
            vent_settings['mode'] = "prvc"
        elif self.ventilator_mode == 3:
            vent_settings['mode'] = "hfov"
            
        return vent_settings
    
    def get_ventilator_output(self):
        vent_output = {}
        
        vent_output['minute volume'] = self.exhaled_minute_volume * 1000
        vent_output['exp_tidal_volume'] = self.expiratory_tidal_volume * 1000
        vent_output['insp time'] = self.t_in
        vent_output['frequency'] = self.measured_freq
        vent_output['pip'] = self.pip 
        vent_output['peep'] = self.peep 
        
        return vent_output
            
