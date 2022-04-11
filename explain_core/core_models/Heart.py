import math

class Heart:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # dependent properties (accessible from outside)
        self.aaf = 0.0
        self.aaf_old = 0.0
        self.aaf_exp = 0.0
        self.vaf = 0.0
        self.vaf_old = 0.0
        self.vaf_exp = 0.0

        self.aaf10 = 0.0
        self.vaf10 = 0.0

        # systolic or diastolic state, 0 = diastolic, 1 = systolic
        self.state = 0 

        # store a reference to the rest of the model
        self.model = model

        # get the modeling stepsize from the model
        self._t = model.modeling_stepsize

    def model_step(self):
        if (self.is_enabled):
            self.model_cycle()

    def model_cycle(self):
        self.ecg_model = self.model.components['ecg']

        # get the relevant timings from the ecg model
        ncc_atrial = self.ecg_model.ncc_atrial
        atrial_duration = self.ecg_model.pq_time
        ncc_ventricular = self.ecg_model.ncc_ventricular
        ventricular_duration = (self.ecg_model.cqt_time + self.ecg_model.qrs_time)

        a_atrium = 10.0
        # varying elastance activation function of the atria
        if ncc_atrial >= 0 and (ncc_atrial < atrial_duration / self._t):
            # the atrial activation curve consists of two gaussian curves on top of each other
            # gaussian curve => y = a * exp(-((t - b) / c)^2) where
            # a = height
            # b = position of the peak
            # c = atrial duration

            a = 1.0
            b = 0.5 * atrial_duration
            c = 0.2 * atrial_duration
            t = ncc_atrial * self._t
            
            self.aaf = a * math.exp(-math.pow((t - b) / c, 2))

        # varying elastance activation function of the ventricles
        if ncc_ventricular >= 0 and (ncc_ventricular < ventricular_duration / self._t):
            # the ventricular activation curve consists of two gaussian curves on top of each other
            # gaussian curve => y = a * exp(-((t - b) / c)^2) where
            # a = height
            # b = position of the peak
            # c = atrial duration

            a1 = 0.5
            b1 = 0.5 * ventricular_duration
            c1 = 0.2 * ventricular_duration
            
            a2 = 0.59
            b2 = 0.6 * ventricular_duration
            c2 = 0.13 * ventricular_duration
            
            t = ncc_ventricular * self._t
            vaf1 = a1 * math.exp(-math.pow((t - b1) / c1, 2))
            vaf2 = a2 * math.exp(-math.pow((t - b2) / c2, 2))
            
            self.vaf = vaf1 + vaf2

            # set the state as systolic
            self.state = 1
        else:
            # set the state as diastolic
            self.state = 0

        # transfer the activation function to the heart compartments and the coronaries
        for ra in self.right_atrium:
            self.model.components[ra].varying_elastance_factor = self.aaf

        for la in self.left_atrium:
            self.model.components[la].varying_elastance_factor = self.aaf

        for rv in self.right_ventricle:
            self.model.components[rv].varying_elastance_factor = self.vaf

        for lv in self.left_ventricle:
            self.model.components[lv].varying_elastance_factor = self.vaf

        for cor in self.coronaries:
            self.model.components[cor].varying_elastance_factor = self.vaf
    
