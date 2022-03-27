import math

class IntrathoracicPressure:
    def __init__(self, model, **args):
        # initialize the super class
        super().__init__()
        
        # initialize a dictionary holding the targets 
        self.targets = {}
        
        # set the independent properties
        for key, value in args.items():
            setattr(self, key, value)
        
        # define the dependent properties
        self.pres = 0
        
        # store a reference to the rest of the model
        self.model = model

        # get the modeling stepsize from the model
        self.t = model.modeling_stepsize
        
    # this method is called by the model engine in every model step
    def model_step (self):
        # during every model step the transmural pressure is calculates
        if self.is_enabled:
            self.calculate()

    def calculate (self):
        # calculate the intrathoracic pressure
        cum_pres = 0
        counter = 0
        
        for source in self.sources:
            cum_pres += self.model.components[source].pres
            counter +=1
    
        self.pres = cum_pres / counter
            
        # apply the mean intrathoracic pressure to the targets
        for target, value in self.targets.items():
            self.model.components[target].pres_itp = (value * self.pres)