/* eslint-disable */

class Resuscitation {
  constructor(_model) {
    this._model = _model;
    this._comp_counter = 0;
    this._resp_counter = 0;
    this.p_max = 60;
    this.p_min = 0;
    this.f_comp = 2;
    this.f_resp = 0.5;
    this.ratio_comp = 3;
    this.ratio_resp = 1;
    this.AA_pres_1 = 10;
  }

  modelStep() {
    if (this.is_enabled) {
      this.modelCycle();
    }
  }

  modelCycle() {
    // Model sinus function
    let a_sinus = (this.p_max - this.p_min) / 2;
    let b_sinus = (this.p_max + this.p_min) / 2;
    let c_sinus = 2 * Math.PI * this.f_comp;
    let sinus   = a_sinus + b_sinus * Math.sin(c_sinus * this._comp_counter - 0.5 * Math.PI);

    this.compressions = sinus;

    // Chest compressions
    // if (this._comp_counter <= (this.ratio_comp/this.f_comp)){

      // apply
      this._model.components["AA"].pres_ext = 0.8 * sinus;
      this._model.components["AARCH"].pres_ext = 0.8 * sinus;
      this._model.components["VCII"].pres_ext = 0.8 * sinus;
      this._model.components["APC"].pres_ext = 0.8 * sinus;
      this._model.components["LL"].pres_ext = 0.8 * sinus;
      this._model.components["LR"].pres_ext = 0.8 * sinus;
      this._model.components["PV"].pres_ext = 0.8 * sinus;
      this._model.components["LA"].pres_ext = 1.0 * sinus;
      this._model.components["RA"].pres_ext = 1.0 * sinus;
      this._model.components["LV"].pres_ext = 1.0 * sinus;
      this._model.components["RV"].pres_ext = 1.0 * sinus;

      // update counter
      this._comp_counter += this._model.modeling_stepsize;

      if (this._comp_counter > 0.5) {
        this._comp_counter = 0
        this._model.components.ECG.ncc_ventricular = 0
      }
    // }

    // Respiration
    //else if (this._resp_counter <=(ratio_resp/f_resp)){
      // ventilator aanzetten
      //this._model.components['ventilator'].is_enabled  = true 

      // update counter
      //this._resp_counter += this._model["modeling stepsize"];
    //}
    //else if (this._resp_counter >=(ratio_resp/f_resp)){
      // ventilator uitzetten
      //this._model.components['ventilator'].is_enabled  = false
    //}

    // reset counter if needed
    // if (this._comp_counter >= (this.ratio_comp/this.f_comp) && this._resp_counter >= (this.ratio_resp/this.f_resp)){
    //   this._comp_counter = 0;
    //   this._resp_counter = 0;
    // }
  }
}