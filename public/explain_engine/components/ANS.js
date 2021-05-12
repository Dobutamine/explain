/* eslint-disable */

class ANS {
  constructor (_model) {
      // declare the instance variables
      this._model = _model;

      // the ans updates not every model cycle but has it's own update frequency
      this._update_timer = 0;
      this.ans_update_interval = 0.015;

      // declare the independent parameters (should be localized in the JSON but for this )
      this._Gv = 0.040 //.112    // gain of heart period T for the vagal activity (mmHg^-1)
      this._Gs = 0.020 //0.060    // gain of heart period T for the sympathetic activity (mmHg^-1)
      this._Tmin = 0.3    // minimal heart period
      this._Tmax = 1.129  // maximal heart period
      this._Dv = 0.8      // pure time delay vagal pathway (s)
      this._Ds = 3.0      // pure time delay sympathetic pathway
      this._tau_v = 0.8   // vagal time constant (s)
      this._tau_s = 10  // sympathetic time constant (s)
      this._Psan = 81 // 57.3 // normal mean value of systemic arterial pressure (mmHg)
      this._S_0 = 1.0     // slope of the sigmoidal curve at it's central point
      
      // calculated independent parameters
      this._k = (this._Tmax - this._Tmin) / (4 * this._S_0)

      // declare the dependent parameters
      this._vagal = 0
      this._sympathetic = 0
      this._dx_vagal = 0
      this._dx_sympathetic = 0
      
      // declare the pure time delay arrays
      this._vagalPsaArrayLength = Math.round(this._Dv / this.ans_update_interval)
      this._vagalPsaArray = new Array(this._vagalPsaArrayLength).fill(this._Psan)
      this._sympatheticPsaArrayLength = Math.round(this._Ds / this.ans_update_interval)
      this._sympatheticPsaArray = new Array(this._sympatheticPsaArrayLength).fill(this._Psan)
  }

  modelStep() {
      
      // if enabled then update the update timer
      if (this.is_enabled) {
          if (this._update_timer > this.ans_update_interval) {
              this._update_timer = 0
              this.modelCycle();
          }
          this._update_timer += this._model.modeling_stepsize
      }
    }

  modelCycle() {
      // get the current modeling stepsize from the model (s)
      const _t = this.ans_update_interval

      // get the current the mean blood pressure from the model (mmHg)
      let _Psa = this._model.components.Monitor.abp_mean

      // guard the Psa for not being undefined or zero
      if (_Psa === 0 | _Psa === undefined) {
          _Psa = this._Psan
      }

      // store the Psa into the delay arrays and shift the arrays
      this._vagalPsaArray.push(_Psa)
      this._vagalPsaArray.splice(0, 1)

      this._sympatheticPsaArray.push(_Psa)
      this._sympatheticPsaArray.splice(0,1)

      // calculate the distance from the operating point and multiply with the gain
      this._vagal = this._Gv * (this._vagalPsaArray[0] - this._Psan)
      this._sympathetic = this._Gs * (this._sympatheticPsaArray[0] - this._Psan)

      // calculate the dx/dt for the vagal and sympathetic nerves and incorporate the time constant
      this._dx_vagal = _t * (1 / this._tau_v) * (-this._dx_vagal + this._vagal) + this._dx_vagal
      this._dx_sympathetic = _t * (1 / this._tau_s) * (-this._dx_sympathetic + this._sympathetic) + this._dx_sympathetic

      // calculate the total dx
      this._dx = this._dx_vagal + this._dx_sympathetic

      // calculate the new heartrate depending on the dx
      this._newHeartPeriod = (this._Tmin + this._Tmax * Math.exp(this._dx / this._k)) / (1 + Math.exp(this._dx / this._k)) // sigmoidal curve
      
      // calculate the new heartrate
      this.heart_rate = 60 / this._newHeartPeriod
      this._model.components.ECG.heart_rate = this.heart_rate
  }
}





/*
class ANS {
  constructor(_model) {
    // declare the instance variables
    this._model = _model;
    this._update_timer = 0;
    this.ans_update_interval = 0.015;

    this._Gv = 0.112; // * maximal gain of heart period T for the vagal activity (mmHg^-1) - intact (not vagotomized) - 4x original value
    this._Gs = 0.060; // * maximal gain of heart period T for the sympathetic activity (mmHg^-1) - intact (not vagotomized) - 4x original value
    this._Tmin = 0.300;// original 0.558; // adjusted 0.273; // minimal heart period (s)
    this._Tmax = 1.20; // original 1.308; // adjusted 1.173; // maximal heart period (s)
    this._Dv = 0.5; // pure time delay vagal pathway (s)
    this._Ds = 3; // pure time delay sympathetic pathway (s)
    this._tau_v = 0.8; // vagal time constant (s)
    this._tau_s = 1.8; // sympathetic time constant (s)
    this._Psan = 81; //144; // *  normal mean value of systemic arterial pressure (mmHg)
    this._S_0 = 1; // slope of the sigmoidal curve at its central point, 1 in basal conditions
		// (sensitivity of the sinus node to sympathetic and vagal stimulation)
    this._k = (this._Tmax - this._Tmin) / (4 * this._S_0);

    // initialization
    this._x_vagal = 0; 
    this._x_sympathetic = 0;

    // Vagal and sympathetic array for pure delay, index 0 is v(t-Dt) and end is v(t)
    this._vagalArrayLength = Math.round(this._Dv / this.ans_update_interval);
    this._sympatheticArrayLength = Math.round(this._Ds / this.ans_update_interval);
    this._vagalArray = new Array(this._vagalArrayLength).fill(0) // fill array with zeros, since vt=0 if Psa=Psan
    this._sympatheticArray = new Array(this._sympatheticArrayLength).fill(0)
  }

  modelStep() {
    if (this.is_enabled) {
      if (this._update_timer >= this.ans_update_interval) {
        this._update_timer = 0;
        this.modelCycle();
      }
      this._update_timer += this._model.modeling_stepsize;
    }
  }

  modelCycle() {
    this._dt = this._model.ans_update_interval // stepsize in seconds
    this._Psa = this._model.components.Monitor.abp_mean
    if (this._Psa == 0) {     // prevent that Psa is 0 in the beginning, but equal to Psan instead
      this._Psa = this._Psan; 
    }

    this._vagal = this._Gv * (this._Psa - this._Psan) // vagal
	  this._sympathetic = this._Gs * (this._Psa - this._Psan) // sympathetical
		this._dx_vagal = 1 / this._tau_v * (this._vagalArray[0] - this._x_vagal) // vagal dx/dt
		this._dx_sympathetic = 1 / this._tau_s * (this._sympatheticArray[0] - this._x_sympathetic) // sympathetic dx/dt
		this._x_vagal += this._dx_vagal * this._dt // Euler forward
		this._x_sympathetic += this._dx_sympathetic * this._dt // Euler forward
		this._x = this._x_vagal + this._x_sympathetic
		this._T = (this._Tmin + this._Tmax * Math.exp(this._x / this._k)) / (1 + Math.exp(this._x / this._k)) // sigmoidal curve
    this.heart_rate = 60 / this._T 
    this._model.components.ECG.heart_rate = this.heart_rate

    // Update vagal and sympathetic array
    this._vagalArray.splice(0,1); // Removes the first element of the array (so removes the current v(t-Dv))
    this._vagalArray.push(this._vagal); // Adds the current value of v(t) to the array (at the end)
    this._sympatheticArray.splice(0,1); 
    this._sympatheticArray.push(this._sympathetic); 

    //logging
    //console.log(this._Psa)
    //console.log(this._x)
  }
}
*/