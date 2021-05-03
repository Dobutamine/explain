<template>
  <q-card class="q-pb-es q-pt-es q-ma-sm" bordered>

    <div class="row q-mt-es">
      <div class="q-gutter-es q-mt-es row gutter text-overline" @click="isEnabled = !isEnabled">
        monitoring
    </div>
    <div v-if="parameters.length > 0" class="row q-mt-es">
      <div class="row">
            <div v-for="(field, index) in parameters" :key='index'>
                <q-input class="col" v-model="field.result" filled dense square :label="field.label" />
            </div>
        </div>
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
      parameters: [],
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

        this.parameters = data.Monitor.parameters
      }
    }
  }

}
</script>

<style>

</style>
