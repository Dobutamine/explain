/* eslint-disable */

class IV {
    constructor(_model) {
      this._model = _model;

      this._administration_stepsize = 0
      this._administration_counter = 0
      this._administration_enabled = false
    }
  
    modelStep() {
      if (this.is_enabled) {
        this.modelCycle();
      }
    }
    
    administerFluidBolus(args) {
        // calculate the stepsize
        this._administration_volume = args[0]
        this._administration_stepsize = args[0] / (args[1] / this._model.modeling_stepsize)
        this._administration_counter = 0
        this._administration_target = args[2]
        this._administration_enabled = true
        console.log(args)
    }

    modelCycle() {
        if (this._administration_enabled) {
            this._administration_volume -= this._administration_stepsize
            if (this._administration_volume < 0) {
                this._administration_stepsize = 0
                this._administration_volume = 0
                this._administration_enabled = false
                console.log('ready')
            }
    
            this._model.components[this._administration_target].vol += this._administration_stepsize
        }
       

    }
  }
  