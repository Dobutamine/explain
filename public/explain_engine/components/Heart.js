/* eslint-disable */
class Heart {
  constructor(_model) {

    // state properties (accessible from outside)
    this.aaf = 0.0
    this.vaf = 0.0

    this.prev_aaf = 0.0
    this.prev_vaf = 0.0

    this.systole = 0
    this.systole_counter = 0
    this.diastole_counter = 0
    this.diastole = 0

    // local state properties
    this._model = _model;
  }

  modelStep() {
    if (this.is_enabled) {
      this.modelCycle();
    }
  }

  // the model step function is called during every step of the model
  modelCycle() {
    const t = this._model["modeling_stepsize"];
    
    // get the relevant timings from the ecg model
    let ncc_atrial = this._model.components.ECG["ncc_atrial"]
    let atrial_duration = this._model.components.ECG["pq_time"] 
    let ncc_ventricular = this._model.components.ECG["ncc_ventricular"]
    let ventricular_duration = (this._model.components.ECG["cqt_time"] + this._model.components.ECG["qrs_time"])

    // varying elastance activation function of the atria
    if (ncc_atrial >= 0 && ncc_atrial < (atrial_duration / t)) {
      this.aaf = Math.pow(Math.sin(Math.PI * (ncc_atrial / atrial_duration) * t), 2);
    } else {
      this.aaf = 0;
    }

    // varying elastance activation function of the ventricles
    if (ncc_ventricular >= 0 && ncc_ventricular < (ventricular_duration / t)) {
      this.vaf = Math.pow(Math.sin(Math.PI * (ncc_ventricular / ventricular_duration) * t), 2);
    } else {
      this.vaf = 0;
    }

    // if (this.prev_vaf >= this.vaf) {
    //   this.systole_counter = 0
    //   this.diastole_counter += 1
    // } else {
    //   this.diastole_counter = 0
    //   this.systole_counter += 1
    // }

    this.prev_vaf = this.vaf
    // check whether we're in systole or diastole


    // increase the atrial and ventricular activation function timers
    this._model.components.ECG["ncc_atrial"] += 1;
    this._model.components.ECG["ncc_ventricular"] += 1;

    // transfer the activation function to the heart compartments
    this._model.components["RA"].el_act = this.aaf;
    this._model.components["RV"].el_act = this.vaf;
    this._model.components["LA"].el_act = this.aaf;
    this._model.components["LV"].el_act = this.vaf;

  }
}
