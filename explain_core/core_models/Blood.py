import math

class Blood:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # set the brent root finding properties
        self.brent_accuracy = 1e-8
        self.max_iterations = 100.0
        self.steps = 0
        
        # acidbase constants
        self.kw = math.pow (10.0, -13.6) * 1000.0
        self.kc = math.pow(10.0, -6.1) * 1000.0
        self.kd = math.pow(10.0, -10.22) * 1000.0
        self.alpha_co2p = 0.03067
        self.left_hp = math.pow(10.0, -7.8) * 1000.0
        self.right_hp = math.pow(10.0, -6.8) * 1000.0
        
        # oxygenation constants
        self.left_o2 = 0.01
        self.right_o2 = 100
        self.alpha_o2p = 0.0095
        self.mmoltoml = 22.2674
        
        # define the independent properties
        # - global
        self.circulating_blood_compounds = {}
        self.fixed_blood_compounds = {}
        
        # - acidbase
        self.sid = 41.6
        self.albumin = 30
        self.phosphates = 1.8
        self.uma = 4
        
        # - oxygenation
        self.dpg = 5
        self.hemoglobin = 10
        self.temp = 37
        
        # define the dependent properties
        # - acidbase
        self.tco2 = 24.9
        self.pco2 = 45
        self.ph = 7.40
        self.hco3 = 25
        self.cco3 = 0
        self.cco2 = 0
        self.be = 0
        
        # - oxygenation
        self.to2 = 9.1
        self.po2 = 75
        self.so2 = 0.98
        
        # set the independent properties from the JSON file. This overwrites previous properties with values form the JSON file
        for key, value in args.items():
            setattr(self, key, value)
            
        # get a reference to the whole model
        self.model = model
        
        # define a list which contains all components holding a blood volume
        self.blood_components = []
        
        self.counter = 0
        
        # now transform the components with content blood into oxygenation and acidbase capable components
        for comp_name, comp in model.components.items():
            if hasattr(comp, 'content'):
                if (comp.content == 'blood'):
                    
                    # sets the p_atm independent variable as property
                    setattr(comp, 'p_atm', self.p_atm)
                    
                    # add a reference to the component to the blood components list
                    self.blood_components.append(comp)

                    # set the blood compounds as properties of the model component
                    for compound, value in self.compounds.items():
                        comp.compounds[compound] = value
                    
                    # set the fixed blood compounds as properties of the model component
                    for compound, value in self.fixed_blood_compounds.items():
                        setattr(comp, compound, value)

                    # set the circulating blood compounds as properties of the model component
                    for compound, value in self.circulating_blood_compounds.items():
                        setattr(comp, compound, value)
                    
                    # set the additional acidbase properties of the model component
                    setattr(comp, "acidbase_enabled", False)
                    setattr(comp, "pco2", self.pco2)
                    setattr(comp, "ph", self.ph)
                    setattr(comp, "hco3", self.hco3)
                    setattr(comp, "be", self.be)
                    
                    # set the additional oxygenation properties of the model component
                    setattr(comp, "oxy_enabled", False)
                    setattr(comp, "po2", self.po2)
                    setattr(comp, "so2", self.so2)
                    setattr(comp, "temp", self.temp)    
                    
                    # the blood containing component is now transformed into a component with oxygenation and acidbase capabilities
                 
    def model_step(self):
        if (self.is_enabled):
            if (self.counter > 5):
                # iterate over all blood components
                for comp in self.blood_components:
                    # if this component has the acidbase enabled then do the calculations
                    if (comp.acidbase_enabled):
                        self.acidbase(comp)

                    # if this component has the oxygenation enabled then do the calculations
                    if (comp.oxy_enabled):
                        self.oxygenation(comp)
                self.counter = 0
            self.counter += 1
    
    def acidbase_from_pco2(self, ph_measured, pco2_measured, hco3_measured, be_measured, sodium, potassium, calcium, magnesium, chloride, lactate, urate, albumin, phosphates, hemoglobin, uma):
        # calcuilate the apparent SID
        self.sid = sodium + potassium + 2 * calcium + 2 * magnesium - chloride - lactate - urate
        
        # get the albumin concentration in g/l
        self.albumin = albumin
        
        # get the inorganic phosphates concentration in mEq/l
        self.phosphates = phosphates
        
        # get the unmeasured anions in mEq/l
        self.uma = uma
        
        # get the total co2 concentration in mmol/l
        self.pco2 = pco2_measured
        
        # get the hemoglobin concentration in mmol/l
        self.hemoglobin = hemoglobin
        
        # now try to find the hydrogen concentration at the point where the net charge of the plasma is zero within limits of the brent accuracy
        hp = self.brent_root_finding(self.net_charge_plasma_from_pco2, self.left_hp, self.right_hp, self.max_iterations, self.brent_accuracy)
        
        # if this hydrogen concentration is found then store it inside the compartment
        if (hp > 0):
            bloodgas = {
                "ph_measured": ph_measured,
                "pco2_measured": pco2_measured,
                "hco3_measured": hco3_measured,
                "sodium": sodium,
                "potassium":potassium,
                "calcium":calcium,
                "magnesium": magnesium,
                "chloride": chloride,
                "lactate": lactate,
                "urate":urate,
                "albumin": albumin,
                "phosphates": phosphates,
                "hemoglobin": hemoglobin,
                "uma": uma,
                "ph_calculated": -math.log10(hp / 1000),
                "hco3_calculated": self.hco3,
                "be_calculated": self.be
            }
            return bloodgas
        else:
            print("no solution found!")
        
        
    def acidbase(self, comp):        
        # calculate the apparent strong ion difference (SID) in mEq/l
        comp.sid = comp.sodium + comp.potassium + 2 * comp.calcium + 2 * comp.magnesium - comp.chloride - comp.lactate - comp.urate
        
        # store the apparent SID
        self.sid = comp.sid
        
        # get the albumin concentration in g/l
        self.albumin = comp.albumin
        
        # get the inorganic phosphates concentration in mEq/l
        self.phosphates = comp.phosphates
        
        # get the unmeasured anions in mEq/l
        self.uma = comp.uma
        
        # get the total co2 concentration in mmol/l
        self.tco2 = comp.tco2
        
        # get the hemoglobin concentration in mmol/l
        self.hemoglobin = comp.hemoglobin
        
        # now try to find the hydrogen concentration at the point where the net charge of the plasma is zero within limits of the brent accuracy
        hp = self.brent_root_finding(self.net_charge_plasma, self.left_hp, self.right_hp, self.max_iterations, self.brent_accuracy)
        
        # if this hydrogen concentration is found then store it inside the compartment
        if (hp > 0):
            # calculate the pH and store it inside the compartment
            comp.ph = (-math.log10(hp / 1000))
            # get the rest of the calculated blood gas
            comp.pco2 = self.pco2
            comp.hco3 = self.hco3
            comp.cco2 = self.cco2
            comp.cco3 = self.cco3
            comp.be = self.be
    
    def net_charge_plasma_from_pco2(self, hp_estimate):
        # calculate the ph based on the current hp estimate
        ph = -math.log10(hp_estimate / 1000.0)
        
        # we do know the total co2 concentration but we now have to find out the distribution of the co2 where tco2 = cco2 + hco3 + cco3
        
        # cco2 = plasma concentration of co2 -> charge neutral
        # hco3 = plasma concentration of bicarbonate -> charge 1-
        # cco3 = plasma concentration of carbonate -> charge 2-
        
        # the distribution is described by 
        # pH = pKc * HCO3 + log10(hco3 / cco2)
        # pH = pKd + log10(cco3 / hco3)
        
        
        # calculate the plasma co2 concentration based on the total co2 in the plasma, hydrogen concentration and the constants Kc and Kd
        cco2p = self.pco2 * self.alpha_co2p
        
        # calculate the plasma hco3(-) concentration (bicarbonate)
        hco3p = (self.kc * cco2p) / hp_estimate
        
        # calculate the plasma co3(2-) concentration (carbonate)
        co3p = (self.kd * hco3p) / hp_estimate
        
        # calculate the plasma OH(-) concentration (water dissociation)
        ohp = self.kw / hp_estimate
        
        # calculate the weak acids (albumin and phosphates)
        # Clin Biochem Rev 2009 May; 30(2): 41-54
        a_base = self.albumin * (0.123 * ph - 0.631) + self.phosphates * (0.309 * ph - 0.469)
        # alb_base = self.albumin * (0.378 / (1.0 + math.pow(10, 7.1 - ph)))
        # phos_base = self.phosphates / (1.0 + math.pow(10, 6.8 - ph))
        
        # calculate the net charge of the plasma. If the netcharge is zero than the current hp_estimate is the correct one.
        netcharge = hp_estimate + self.sid - hco3p - 2.0 * co3p - ohp - a_base - self.uma
        
        # calculate the base excess according to the van Slyke equation
        self.be = (hco3p - 24.4 + (2.3 * self.hemoglobin + 7.7) * (ph - 7.4)) * (1.0 - 0.023 * self.hemoglobin)
        
        # calculate the pco2 and store the plasma hco3
        self.hco3 = hco3p
        self.cco3 = co3p
        self.cco2 = cco2p
        
        # return the net charge to the brent function
        return netcharge
        
    def net_charge_plasma(self, hp_estimate):
        # calculate the ph based on the current hp estimate
        ph = -math.log10(hp_estimate / 1000.0)
        
        # we do know the total co2 concentration but we now have to find out the distribution of the co2 where tco2 = cco2 + hco3 + cco3
        
        # cco2 = plasma concentration of co2 -> charge neutral
        # hco3 = plasma concentration of bicarbonate -> charge 1-
        # cco3 = plasma concentration of carbonate -> charge 2-
        
        # the distribution is described by 
        # pH = pKc * HCO3 + log10(hco3 / cco2)
        # pH = pKd + log10(cco3 / hco3)
        
        
        # calculate the plasma co2 concentration based on the total co2 in the plasma, hydrogen concentration and the constants Kc and Kd
        cco2p = self.tco2 / (1.0 + self.kc / hp_estimate + (self.kc * self.kd) / math.pow(hp_estimate, 2.0))
        
        # calculate the plasma hco3(-) concentration (bicarbonate)
        hco3p = (self.kc * cco2p) / hp_estimate
        
        # calculate the plasma co3(2-) concentration (carbonate)
        co3p = (self.kd * hco3p) / hp_estimate
        
        # calculate the plasma OH(-) concentration (water dissociation)
        ohp = self.kw / hp_estimate
        
        # calculate the pco2 of the plasma
        pco2p = cco2p / self.alpha_co2p
        
        # calculate the weak acids (albumin and phosphates)
        # Clin Biochem Rev 2009 May; 30(2): 41-54
        a_base = self.albumin * (0.123 * ph - 0.631) + self.phosphates * (0.309 * ph - 0.469)
        # alb_base = self.albumin * (0.378 / (1.0 + math.pow(10, 7.1 - ph)))
        # phos_base = self.phosphates / (1.0 + math.pow(10, 6.8 - ph))
        
        # calculate the net charge of the plasma. If the netcharge is zero than the current hp_estimate is the correct one.
        netcharge = hp_estimate + self.sid - hco3p - 2.0 * co3p - ohp - a_base - self.uma
        
        # calculate the base excess according to the van Slyke equation
        self.be = (hco3p - 24.4 + (2.3 * self.hemoglobin + 7.7) * (ph - 7.4)) * (1.0 - 0.023 * self.hemoglobin)
        
        # calculate the pco2 and store the plasma hco3
        self.pco2 = pco2p
        self.hco3 = hco3p
        self.cco3 = co3p
        self.cco2 = cco2p
        
        # return the net charge to the brent function
        return netcharge
    
    def oxygenation(self, comp):
        # get the for the oxygenation independent parameters from the component
        self.to2 = comp.to2
        self.dpg = comp.dpg
        self.hemoglobin = comp.hemoglobin
        self.be = comp.be
        self.temp = comp.temp
        
        # calculate the po2 from the to2 using a brent root finding function and oxygen dissociation curve
        self.po2 = self.brent_root_finding(self.oxygen_content, self.left_o2, self.right_o2, self.max_iterations, self.brent_accuracy)
        
        # if a po2 is found then store the po2 and so2 into the component
        if (self.po2 > 0):
            # convert the po2 to mmHg
            comp.po2 = self.po2 / 0.1333
            comp.so2 = self.so2 * 100
        
    def oxygen_content (self, po2_estimate):
        # calculate the saturation from the current po2 from the current po2 estimate
        self.so2 = self.oxygen_dissociation_curve(po2_estimate)
        
        # calculate the to2 from the current po2 estimate
        # convert the hemoglobin unit from mmol/l to g/dL
        # convert the po2 from kPa to mmHg
        # convert to output from ml O2/dL blood to ml O2/l blood
        to2_new_estimate = (0.0031 * (po2_estimate / 0.1333) + 1.36 * (self.hemoglobin / 0.6206) * self.so2) * 10.0
        
        # convert the ml O2/l to mmol/l
        to2_new_estimate = to2_new_estimate / self.mmoltoml
        
        # calculate the difference between the real to2 and the to2 based on the new po2 estimate and return it to the brent root finding function
        dto2 = self.to2 - to2_new_estimate
        
        return dto2

    def oxygen_dissociation_curve(self, po2):
        # calculate the saturation from the po2 depending on the ph,be, temperature and dpg level.
        a = 1.04 * (7.4 - self.ph) + 0.005 * self.be + 0.07 * (self.dpg - 5.0)
        b = 0.055 * (self.temp + 273.15 - 310.15)
        y0 = 1.875
        x0 = 1.875 + a + b
        h0 = 3.5 + a
        k = 0.5343
        x = math.log(po2, math.e)
        y = x - x0 + h0 * math.tanh(k * (x - x0)) + y0
        
        # return the o2 saturation
        return 1.0 / (math.pow(math.e, -y) + 1.0)
    
    def brent_root_finding(self, f, x0, x1, max_iter, tolerance):
        self.steps = 0
        
        fx0 = f(x0)
        fx1 = f(x1)
 
        if (fx0 * fx1) > 0:
            return -1
 
        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0
            fx0, fx1 = fx1, fx0
 
        x2, fx2 = x0, fx0
 
        mflag = True
        steps_taken = 0
 
        while steps_taken < max_iter and abs(x1-x0) > tolerance:
            fx0 = f(x0)
            fx1 = f(x1)
            fx2 = f(x2)

            if fx0 != fx2 and fx1 != fx2:
                L0 = (x0 * fx1 * fx2) / ((fx0 - fx1) * (fx0 - fx2))
                L1 = (x1 * fx0 * fx2) / ((fx1 - fx0) * (fx1 - fx2))
                L2 = (x2 * fx1 * fx0) / ((fx2 - fx0) * (fx2 - fx1))
                new = L0 + L1 + L2

            else:
                new = x1 - ( (fx1 * (x1 - x0)) / (fx1 - fx0) )

            if ((new < ((3 * x0 + x1) / 4) or new > x1) or
                (mflag == True and (abs(new - x1)) >= (abs(x1 - x2) / 2)) or
                (mflag == False and (abs(new - x1)) >= (abs(x2 - d) / 2)) or
                (mflag == True and (abs(x1 - x2)) < tolerance) or
                (mflag == False and (abs(x2 - d)) < tolerance)):
                new = (x0 + x1) / 2
                mflag = True

            else:
                mflag = False

            fnew = f(new)
            d, x2 = x2, x1

            if (fx0 * fnew) < 0:
                x1 = new
            else:
                x0 = new

            if abs(fx0) < abs(fx1):
                x0, x1 = x1, x0

            steps_taken += 1
            
        if (steps_taken >= max_iter):
            return -1
        else:
            self.steps = steps_taken
            return x1
    
    
    
    