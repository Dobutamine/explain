/* eslint-disable */

class Resuscitation {
  constructor(_model) {
    this._model = _model;
    this._comp_counter = 0;
    this._resp_counter = 0;
    this.p_max = 100;
    this.p_min = 0;
    this.f_comp = 2;
    this.f_resp = 0.5;
    this.ratio_comp = 3;
    this.ratio_resp = 1;
    this.AA_pres_1 = 10;
  }

  modelStep() {
    if (this.is_enabled) {
      // this.modelCycle();
    }
  }

  modelCycle() {
    // Model sinus function
    let a_sinus = (this.p_max - this.p_min)/2;
    let b_sinus = (this.p_max + this.p_min)/2;
    let c_sinus = 2*Math.PI * this.f_comp;
    let sinus   = a_sinus + b_sinus * Math.sin(c_sinus*this._comp_counter - 0.5*Math.PI);

    this.compressions = sinus;

    // Chest compressions
    if (this._comp_counter <= (this.ratio_comp/this.f_comp)){
      // list of all components that are affected by chest compressions
      let AA_pres     = this._model.components['AA'].pres;
      let AARCH_pres  = this._model.components['AARCH'].pres;
      let VCII_pres   = this._model.components['VCII'].pres;
      let APC_pres    = this._model.components['APC'].pres;
      let LL_pres     = this._model.components['LL'].pres;
      let LR_pres     = this._model.components['LR'].pres;
      let PV_pres     = this._model.components['PV'].pres;
      let LA_pres     = this._model.components['LA'].pres;
      let RA_pres     = this._model.components['RA'].pres;
      let LV_pres     = this._model.components['LV'].pres;
      let RV_pres     = this._model.components['RV'].pres;

      // percentage of pressure applies on these components
      AA_pres     += 0.8 * sinus;
      AARCH_pres  += 0.8 * sinus;
      VCII_pres   += 0.8 * sinus;
      APC_pres    += 0.8 * sinus;
      LL_pres     += 0.8 * sinus;
      LR_pres     += 0.8 * sinus;
      PV_pres     += 0.8 * sinus;
      LA_pres     += 1.0 * sinus;
      RA_pres     += 1.0 * sinus;
      LV_pres     += 1.0 * sinus;
      RV_pres     += 1.0 * sinus;

      // apply
      this._model.components["AA"].pres_ext     = AA_pres;
      this._model.components["AARCH"].pres_ext  = AARCH_pres;
      this._model.components["VCII"].pres_ext   = VCII_pres;
      this._model.components["APC"].pres_ext    = APC_pres;
      this._model.components["LL"].pres_ext     = LL_pres;
      this._model.components["LR"].pres_ext     = LR_pres;
      this._model.components["PV"].pres_ext     = PV_pres;
      this._model.components["LA"].pres_ext     = LA_pres;
      this._model.components["RA"].pres_ext     = RA_pres;
      this._model.components["LV"].pres_ext     = LV_pres;
      this._model.components["RV"].pres_ext     = RV_pres;

      // update counter
      this._comp_counter += this._model.modeling_stepsize;
    }

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
    if (this._comp_counter >= (this.ratio_comp/this.f_comp) && this._resp_counter >= (this.ratio_resp/this.f_resp)){
      this._comp_counter = 0;
      this._resp_counter = 0;
    }
  }
}