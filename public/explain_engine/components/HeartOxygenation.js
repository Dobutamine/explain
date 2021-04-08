/* eslint-disable */

class HeartOxygenation {
    constructor(_model) {
      this._model = _model;
    }
  
    modelStep() {
      if (this.is_enabled) {
        this.modelCycle();
      }
    }
  
    modelCycle() {}
  }