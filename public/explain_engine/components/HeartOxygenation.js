/* eslint-disable */

class HeartOxygenation {
    constructor(_model) {
      this._model = _model;

      this.mso2 = 0;
      this.pva = 0;
      this.mvo2n = 0;
      this.A = 0.000018;
      this.B = 0.0000024;
      this.C = 0.000014;
      // this.alpha = 0.995;
      this.LVW = 0.237;
      this.TVW = 0.316;

      this.mvo2 = 0;
      this.mbo2 = 0;
      this.normMBO2 = 5;

      this.mii = 0;
      this.p = 0.5;

      this.minLVVol = 0
      this.minLVVolTemp = 1

      this.minLVVol = 0
      this.minLVVolTemp = 1

      this.maxLVVol = 0
      this.maxLVVolTemp = 0

      this.pva = 0
    }
  
    modelStep() {
      if (this.is_enabled) {
        this.modelCycle();
      }
    }
  
    modelCycle() {
      // first we need to find the current minimal and maximal left ventricular volumes for the pressure-volume area calculation

      // Get the inputs from the model
      const currentVolume = this._model.components.LV.vol
      const heartrate = this._model.components.ECG.heart_rate
      const LVElMax = this._model.components.LV.el_max
      const LVVolU = this._model.components.LV.vol_u

      // evaluate the minimal and maximal volumes every heartbeat (so when ncc_ventricular is 1)
      if (this._model.components.ECG.ncc_ventricular === 1) {
        // store minimal volume
        this.minLVVol = this.minLVVolTemp
        this.minLVVolTemp = 1
        // store maximal volume
        this.maxLVVol = this.maxLVVolTemp
        this.maxLVVolTemp = 0
      }
      // determine minimal volume
      if (currentVolume < this.minLVVolTemp) {
        this.minLVVolTemp = currentVolume 
      }
      // determine maximal volume
      if (currentVolume > this.maxLVVolTemp) {
        this.maxLVVolTemp = currentVolume 
      }

      // pressure-volume area for a single cardiac cycle per 100 gram of left ventricle (suga et al)
      this.pva = (LVElMax * (this.minLVVol - LVVolU) * (this.maxLVVol - this.minLVVol) + 0.5 * LVElMax * Math.pow((this.minLVVol - LVVolU), 2)) / this.LVW;

      // calculate the myocardial oxygenation consumption normalized to left ventricular weight in ml o2 / 100g
      this.mvo2n = (this.A * this.pva + this.B * LVElMax + this.C) * this.LVW * heartrate


      // we no have the pressure volume area is which determines the left ventricular workload and by that the oxygen use
      // we have to translate this to the fvatp of the coronaries
      // in the steady state the normal pva = 2.46, stored in the this.pva_normal variable of the JSON file



      

      // STEP 1 - Determine the energy need of the myocardium

      // INPUT heartrate, stroke volume
      // OUTPUT fvatp of the COR compartment

       // myocardial oxygen supply in ml O2/min
      //       //mso2 = myDataclass.bcMYO.o2In * 1000;

      // // filter the oxygen supply
      // normMBO2 = normMBO2 + (0.01 * (mso2 - normMBO2));

      // // pressure-volume area for a single cardiac cycle per 100 gram of left ventricle
      // const lvElMax = this._model.components["LV"].el_max

      // let pva = (myDataclass.bcLV.ElContractionBaseline * (myDataclass.bcLV.VolMin - myDataclass.bcLV.Uvol) * (myDataclass.bcLV.VolMax - myDataclass.bcLV.VolMin) + 0.5 * myDataclass.bcLV.ElContractionBaseline * Math.Pow((myDataclass.bcLV.VolMin - myDataclass.bcLV.Uvol), 2)) / LVW;

      // // myocardial oxygen consumption, normalized to left ventricle weigth in ml O2 / 100g
      // mvo2n = A * pva + B * myDataclass.bcLV.ElContractionBaseline + C;

      //       // total myocardial oxygen consumption in ml O2 / min
      //       mvo2 = (mvo2n * TVW) * myDataclass.Heartrate;

      //       // add the oxygen consumption to the VO2 as the myocardium is the only compartment with a dynamic oxygen consumption
      //       myDataclass.VO2 = (mvo2 / 60) + myDataclass.VO2WithoutMyo;

      //       // store mvo2 in dataclass
      //       myDataclass.MyoO2Use = mvo2;

      //       // myocardial oxygen balance
      //       mbo2 = normMBO2 / mvo2;

      //       // myocardial ischemia index
      //       mii = mbo2 / 2;
      

      // STEP 2 - Determine the energy balance of the heart
      // INPUT energy deficit from the energybalance of the LV

      // OUTPUT decreasing stroke volume by decreasing el_max
      
    }
  }