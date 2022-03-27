import math

class Valve:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()

        # properties
        self.name = ""            # name of the resistor
        self.type = "resistor"    # type of the model component
        self.subtype = "blood"    # subtype of the model component.
        self.is_enabled = True    # determines whether or not the resistor is enabled
        self.no_flow = False      # determines whether the resistor allows any flow
        self.no_backflow = False  # determines whether the resistor allows backflow
        self.comp_from = ""       # holds the name of the first compliance wich the resistor connects
        self.comp_to = ""         # holds the name of the second compliance which the resistor connects
        self.r_for = 1            # holds the resistance if the flow direction is from comp_from to comp_to
        self.r_for_fac = 1.0      # holds the factor with which r_for is multiplied
        self.r_back = 1           # holds the resistance if the flow direction is from comp_to to comp_from
        self.r_back_fac = 1.0     # holds the factor with which r_for is multiplied
        self.k = 0                # holds the constant for the non-linear flow dependency of the resistance
        self.k_fac = 1            # holds the r_k multiplier
        self.flow = 0


        # fill the properties with the desired values
        for key, value in args.items():
            setattr(self, key, value)

        comp_from_found = False
        comp_to_found = False

        # store a reference to the compliances which this resistor 'connects'
        if self.comp_from in model.components:
            self.comp1 = model.components[self.comp_from]
            comp_from_found = True

        if self.comp_to in model.components:
            self.comp2 = model.components[self.comp_to]
            comp_to_found = True

        if (comp_from_found == False):
            print('Resistor', self.name, 'could not find compliance/time_varying_elastance', self.comp_from)

        if (comp_to_found == False):
            print('Resistor', self.name, 'could not find compliance/time_varying_elastance', self.comp_to)

        # get the modeling stepsize from the model
        self.t = model.modeling_stepsize

        # initialize the dependent properties
        self.flow = 0
        self.resistance = 0

    def model_step (self):
        self.calculate_flow()
        
    def calculate_resistance(self, p1, p2):
        # calculate the flow dependent parts of the resistance
        nonlin_fac = self.r_k * self.k_fac * abs(self.flow)

        if (p1 > p2):
            return self.r_for * self.r_for_fac + nonlin_fac
        else:
            return self.r_back * self.r_back_fac + nonlin_fac
            
            

    def calculate_flow(self):
        if self.is_enabled:
            # get the pressures from comp1 and comp2
            p1 = self.comp1.pres
            p2 = self.comp2.pres

            # calculate the resistance
            self.resistance = self.calculate_resistance(p1, p2)

            # first check whether the no_flow flag is checked
            if (self.no_flow):
                self.flow = 0
            else:
                self.flow = (p1 - p2) / self.resistance
                # check whether backflow is allowed across this resistor
                if (self.flow < 0 and self.no_backflow):
                    self.flow = 0

            # now we have the flow in l/sec and we have to convert it to l by multiplying it by the modeling_stepsize
            dvol = self.flow * self.t

            # change the volumes of the compliances
            if (dvol > 0):
                # positive value means comp1 loses volume and comp2 gains volume
                self.comp1.volume_out(dvol, self.comp2)
                self.comp2.volume_in(dvol, self.comp1)
            else:
                # negative value means comp1 gains volume and comp2 loses volume
                self.comp1.volume_in(-dvol, self.comp2)
                self.comp2.volume_out(-dvol, self.comp1)
        else:
            self.flow = 0