/* eslint-disable */

class Metabolism {
  constructor(_model) {
    this._model = _model;

    
  }

  modelStep() {
    if (this.is_enabled) {
        this.modelCycle();
    }
  }

  modelCycle() {
    // distribute the energy use of the model over the different compartments
    // console.log(this.active_comps)
  }

  calcEnergyUse() {

    const fvatp = this.fvatp

    if (fvatp > 0 ) {
      // get the local ATP need in molecules per second
      let atp_need = fvatp * this._model.components.Metabolism.atp_need;

      // new we need to know how much molecules ATP we need in this step
      let atp_need_step = atp_need * this._model.modeling_stepsize;

      // get the number of oxygen molecules available in this compartment in mmol
      let o2_molecules_available = this.to2 * this.vol;

      // we state that 80% of these molecules are available for use (guess)
      let o2_molecules_available_for_use = 0.8 * o2_molecules_available;

      // how many molecules o2 do we need to burn in this step as 1 mmol of o2 gives 5 mmol of ATP when processed by oxydative phosphorylation
      let o2_to_burn = atp_need_step / 5.0;

      // how many needed ATP molecules can't be produced by aerobic respiration
      let anaerobic_atp = (o2_to_burn - o2_molecules_available_for_use / 4.0) * 5.0;

      // if negative then there are more o2 molecules available than needed and shut down anaerobic fermentation
      if (anaerobic_atp < 0) {
        anaerobic_atp = 0;
      }

      let o2_burned = o2_to_burn;
      // if we need to burn more than we have then burn all available o2 molecules
      if (o2_to_burn > o2_molecules_available_for_use) {
        // burn all available o2 molecules
        o2_burned = o2_molecules_available_for_use;
      }

      // as we burn o2 molecules we have to substract them from the total number of o2 molecules
      o2_molecules_available -= o2_burned;

      // calculate the new TO2
      this.to2 = o2_molecules_available / this.vol;
      // watch for negative concentrations
      if (this.to2 < 0) {
        this.to2 = 0;
      }

      // we now know how much o2 molecules we've burnt so we also know how much co2 we generated depending on the respiratory quotient
      let co2_molecules_produced = o2_burned * this._model.components.Metabolism.resp_q;

      // add the co2 molecules to the total co2 molecules
      this.tco2 = (this.tco2 * this.vol + co2_molecules_produced) / this.vol;
      // watch for negative concentrations
      if (this.tco2 < 0) {
        this.tco2 = 0;
      }
    }
  }

}
