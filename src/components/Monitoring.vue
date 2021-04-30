<template>
  <q-card class="q-pb-es q-pt-es q-ma-sm" bordered>

    <div class="row q-mt-es">
      <div class="q-gutter-es q-mt-es row gutter text-overline" @click="isEnabled = !isEnabled">
        monitoring
    </div>
    <div v-if="isEnabled" class="row q-mt-es">
      <div class="row">
          <q-input class="col" v-model="heartrate" filled dense square label="heartrate" />
          <q-input class="col" v-model="abp" filled dense square label="abp" />
          <q-input class="col" v-model="pap" filled dense square label="pap" />
      </div>
      <div class="row">
          <q-input class="col" v-model="sao2_pre" filled dense square label="sao2 pre" />
          <q-input class="col" v-model="sao2_post" filled dense square label="sao2 post" />
          <q-input class="col" v-model="cvp" filled dense square label="cvp" />
      </div>
      <div class="row">
          <q-input class="col" v-model="resp_rate" filled dense square label="resp rate" />
          <q-input class="col" v-model="etco2" filled dense square label="etco2" />
          <q-input class="col" v-model="temp" filled dense square label="temp" />
      </div>
    </div>
    <q-separator></q-separator>
    <div class="q-gutter-es q-mt-es row gutter text-overline" @click="bloodgasEnabled = !bloodgasEnabled">
          bloodgas
    </div>
    <div v-if="bloodgasEnabled" class="row q-mt-es">
      <div class="row">
            <q-input class="col" v-model="ph" filled dense square label="pH" />
            <q-input class="col" v-model="po2" filled dense square label="pO2" />
            <q-input class="col" v-model="pco2" filled dense square label="pCO2" />
      </div>
    </div>
    <q-separator></q-separator>
    <div class="q-gutter-es q-mt-es row gutter text-overline" @click="hemodynamicEnabled = !hemodynamicEnabled">
          hemodynamic monitor
    </div>
    <div v-if="hemodynamicEnabled" class="row q-mt-es q-mb-md">
        <div class="row">
            <q-input class="col" v-model="ivc_flow" filled dense square label="ivc flow" />
            <q-input class="col" v-model="svc_flow" filled dense square label="svc flow" />
            <q-input class="col" v-model="myo_flow" filled dense square label="cor flow" />
        </div>
        <div class="row">
            <q-input class="col" v-model="pda_flow" filled dense square label="pda flow" />
            <q-input class="col" v-model="ofo_flow" filled dense square label="ofo flow" />
            <q-input class="col" v-model="vsd_flow" filled dense square label="vsd flow" />
        </div>
        <div class="row">
            <q-input class="col" v-model="kidney_flow" filled dense square label="kidney flow" />
            <q-input class="col" v-model="liver_flow" filled dense square label="liver flow" />
            <q-input class="col" v-model="brain_flow" filled dense square label="brain flow" />
        </div>
        <div class="row">
            <q-input class="col" v-model="lvo" filled dense square label="lvo" />
            <q-input class="col" v-model="lv_stroke" filled dense square label="lv stroke" />
            <q-input class="col" v-model="rvo" filled dense square label="rvo" />
        </div>
        <div class="row">
            <q-input class="col" v-model="rv_stroke" filled dense square label="rv stroke" />
            <q-input class="col" v-model="lungshunt_flow" filled dense square label="lung shunt" />
            <q-input class="col" v-model="qpqs" filled dense square label="Qp:Qs" />
        </div>
        <div class="row">
            <q-input class="col" v-model="ecmo_flow" filled dense square label="ecmo_flow" />
            <q-input class="col" v-model="ecinp" filled dense square label="pre oxy pres" />
            <q-input class="col" v-model="ecoutp" filled dense square label="post oxy pres" />
        </div>
      </div>
    </div>
    <q-separator></q-separator>
    <div class="q-gutter-es q-mt-es row gutter text-overline" @click="respiratoryEnabled = !respiratoryEnabled">
          respiratory monitor
    </div>
    <div v-if="respiratoryEnabled" class="row q-mt-es q-mb-md">
        <div class="row">
            <q-input class="col" v-model="resp_rate" filled dense square label="resp reate" />
            <q-input class="col" v-model="tidal_volume" filled dense square label="tidal vol" />
            <q-input class="col" v-model="minute_volume" filled dense square label="minute vol" />
        </div>

    </div>

  </q-card>
</template>

<script>
export default {
  data () {
    return {
      isEnabled: true,
      initialized: false,
      bloodgasEnabled: true,
      hemodynamicEnabled: true,
      respiratoryEnabled: false,
      modelEventListener: null,
      heartrate: '-',
      abp: '-/-',
      pap: '-/-',
      cvp: '-',
      ecinp: '-',
      ecoutp: '-',
      sao2_pre: '-',
      sao2_post: '-',
      resp_rate: '-',
      etco2: '-',
      temp: '-',
      ivc_flow: 0,
      svc_flow: 0,
      myo_flow: 0,
      pda_flow: 0,
      ofo_flow: 0,
      vsd_flow: 0,
      ecmo_flow: 0,
      kidney_flow: 0,
      liver_flow: 0,
      brain_flow: 0,
      ub_flow: 0,
      lb_flow: 0,
      qpqs: 1,
      lungshunt_flow: 0,
      oxy_flow_ub: 0,
      oxy_flow_lb: 0,
      lvo: 0,
      rvo: 0,
      lv_stroke: 0,
      rv_stroke: 0,
      ph: 0,
      po2: 0,
      pco2: 0,
      tidal_volume: 0,
      minute_volume: 0,
      vent_peak_presssure: 0,
      vent_plateau_pressure: 0,
      vent_compliance: 0,
      vent_resistance: 0,
      vent_peep: 0,
      vent_freq: 0,
      vent_minute_volume: 0,
      vent_tidal_volume: 0,
      vent_insp_flow: 0,
      vent_exp_flow: 0,
      vent_insp_time: 0,
      datalogger_data: null,
      rtUpdateFreq: 1,
      prevTime: 0
    }
  },
  mounted () {
    this.modelEventListener = this.$model.engine.addEventListener('message', (message) => {
      switch (message.data.type) {
        case 'data':
          switch (message.data.target) {
            case 'datalogger_output':
              this.updateMonitorRealtime(message.data.data[message.data.data.length - 1])
              break
            default:
              break
          }
          break
        case 'rt':
          this.rt_data = message.data.data
          if (this.isEnabled | this.bloodgasEnabled | this.hemodynamicEnabled | this.respiratoryEnabled) {
            this.updateMonitorRealtime(message.data.data[0])
          }
          break
      }
    })
  },
  beforeDestroy () {
    delete this.modelEventListener
  },
  methods: {
    toggleIsEnabled () {
      this.isEnabled = !this.isEnabled
    },
    updateMonitorDatalogger () {

    },
    checkIsNaN (numberToCheck, rounding) {
      if (typeof numberToCheck !== 'undefined') {
        if (Number.isNaN(numberToCheck)) {
          return '-'
        } else {
          return numberToCheck.toFixed(rounding)
        }
      } else {
        return '-'
      }
    },
    updateMonitorRealtime (data) {
      if (data.time - this.prevTime > 1) {
        this.prevTime = data.time
        console.log(data)
        if (this.isEnabled) {

        }

        if (this.bloodgasEnabled) {

        }

        if (this.hemodynamicEnabled) {
          data.Monitor.parameters.forEach(element => {
            if (element.label === 'lvo') {
              this[element.label] = this.checkIsNaN(element.flow, 4)
              this.lv_stroke = this.checkIsNaN(element.stroke, 4)
            }
            if (element.label === 'rvo') {
              this.rvo = this.checkIsNaN(element.flow, 4)
              this.rv_stroke = this.checkIsNaN(element.stroke, 4)
            }
          })
        }

        if (this.respiratoryEnabled) {

        }
      }
    }
  }

}
</script>

<style>

</style>
