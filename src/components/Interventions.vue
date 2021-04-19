<template>
  <q-card class="q-pb-sm q-pt-es q-ma-sm" bordered>
      <div class="q-ma-es text-overline text-center">
          systemic vascular resistance
      </div>
      <div>
        <q-slider label v-model="svr" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changeSVR"/>
      </div>

      <div class="q-ma-es text-overline text-center" div >
        pulmonary vascular resistance
      </div>
      <div>
        <q-slider label v-model="pvr" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changePVR"/>
      </div>

      <div class="q-ma-es text-overline text-center"  >
        right heart contractility
      </div>
      <div>
        <q-slider label v-model="contractilityRight" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changeContractilityRight"/>
      </div>

      <div class="q-ma-es text-overline text-center"  >
        left heart contractility
      </div>
      <div>
        <q-slider label v-model="contractilityLeft" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changeContractilityLeft"/>
      </div>

      <div class="q-ma-es text-overline text-center"  >
        ductus arteriosus size
      </div>
      <div>
          <q-slider label v-model="pdaSize" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changePDASize"/>
      </div>

      <div class="q-ma-es text-overline text-center"  >
        foramen ovale size
      </div>
      <div>
         <q-slider label v-model="ofoSize" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changeOFOSize"/>
      </div>

      <div class="q-ma-es text-overline text-center"  >
        ventricular septal defect size
      </div>
      <div>
         <q-slider label v-model="vsdSize" dark :min="0" :max="1000" :step="1" color="teal-10" @change="changeVSDSize"/>
      </div>

      <div class="q-ma-es text-overline text-center"  >

      </div>
      <div>
         <q-btn @click="addVolume"  color="teal-7">add 10 ml of volume in 10 seconds</q-btn>
      </div>

  </q-card>
</template>

<script>
export default {
  data () {
    return {
      isEnabled: true,
      svr: 100,
      pvr: 100,
      pdaSize: 0,
      ofoSize: 0,
      vsdSize: 0,
      contractilityRight: 100,
      contractilityLeft: 100
    }
  },
  methods: {
    changeSVR () {
      if (this.svr <= 0) {
        this.svr = 0.1
      }
      const scaling = this.svr / 100

      this.$model.setPropertyDirect('AD_LB', 'r_for_fac', scaling)
      this.$model.setPropertyDirect('AD_LIVSPLE', 'r_for_fac', scaling)
      this.$model.setPropertyDirect('AD_AR', 'r_for_fac', scaling)
      this.$model.setPropertyDirect('AD_INTESTINES', 'r_for_fac', scaling)

      this.$model.setPropertyDirect('AARCH_UB', 'r_for_fac', scaling)
      this.$model.setPropertyDirect('AARCH_BRAIN', 'r_for_fac', scaling)
      this.$model.setPropertyDirect('AA_COR', 'r_for_fac', scaling)

      this.$model.setPropertyDirect('AD_LB', 'r_back_fac', scaling)
      this.$model.setPropertyDirect('AD_LIVSPLE', 'r_back_fac', scaling)
      this.$model.setPropertyDirect('AD_AR', 'r_back_fac', scaling)
      this.$model.setPropertyDirect('AD_INTESTINES', 'r_back_fac', scaling)

      this.$model.setPropertyDirect('AARCH_UB', 'r_back_fac', scaling)
      this.$model.setPropertyDirect('AARCH_BRAIN', 'r_back_fac', scaling)
      this.$model.setPropertyDirect('AA_COR', 'r_back_fac', scaling)
    },
    changePVR () {
      if (this.pvr > 0) {
        const scaling = this.pvr / 100

        this.$model.setPropertyDirect('APC_LL', 'r_for_fac', scaling)
        this.$model.setPropertyDirect('APC_LR', 'r_for_fac', scaling)

        this.$model.setPropertyDirect('APC_LR', 'r_back_fac', scaling)
        this.$model.setPropertyDirect('APC_LR', 'r_back_fac', scaling)
      }
    },
    changeContractilityRight () {
      if (this.contractilityRight > 0) {
        const scaling = this.contractilityRight / 100

        this.$model.setPropertyDirect('RA', 'el_max_fac', scaling)
        this.$model.setPropertyDirect('RV', 'el_max_fac', scaling)
      }
    },
    changeContractilityLeft () {
      if (this.contractilityLeft > 0) {
        const scaling = this.contractilityLeft / 100

        this.$model.setPropertyDirect('LA', 'el_max_fac', scaling)
        this.$model.setPropertyDirect('LV', 'el_max_fac', scaling)
      }
    },
    changePDASize () {
      if (this.pdaSize > 0) {
        const scaling = 100 / this.pdaSize

        this.$model.setPropertyDirect('SHUNT_DA', 'is_enabled', true)
        this.$model.setPropertyDirect('SHUNT_DA', 'r_for_fac', scaling)
        this.$model.setPropertyDirect('SHUNT_DA', 'r_back_fac', scaling)
      } else {
        this.$model.setPropertyDirect('SHUNT_DA', 'is_enabled', false)
        this.$model.setPropertyDirect('SHUNT_DA', 'r_for_fac', 100000)
        this.$model.setPropertyDirect('SHUNT_DA', 'r_back_fac', 100000)
      }
    },
    changeOFOSize () {
      if (this.ofoSize > 0) {
        const scaling = 100 / this.ofoSize

        this.$model.setPropertyDirect('SHUNT_OFO', 'is_enabled', true)
        this.$model.setPropertyDirect('SHUNT_OFO', 'r_for_fac', scaling)
        this.$model.setPropertyDirect('SHUNT_OFO', 'r_back_fac', scaling)
      } else {
        this.$model.setPropertyDirect('SHUNT_OFO', 'is_enabled', false)
        this.$model.setPropertyDirect('SHUNT_OFO', 'r_for_fac', 100000)
        this.$model.setPropertyDirect('SHUNT_OFO', 'r_back_fac', 100000)
      }
    },
    changeVSDSize () {
      if (this.vsdSize > 0) {
        const scaling = 100 / this.vsdSize

        this.$model.setPropertyDirect('SHUNT_VSD', 'is_enabled', true)
        this.$model.setPropertyDirect('SHUNT_VSD', 'r_for_fac', scaling)
        this.$model.setPropertyDirect('SHUNT_VSD', 'r_back_fac', scaling)
      } else {
        this.$model.setPropertyDirect('SHUNT_VSD', 'is_enabled', false)
        this.$model.setPropertyDirect('SHUNT_VSD', 'r_for_fac', 100000)
        this.$model.setPropertyDirect('SHUNT_VSD', 'r_back_fac', 100000)
      }
    },
    addVolume () {
      this.$model.setPropertyByFunction('IV', 'administerFluidBolus', [0.01, 10, 'VCIE'])
    }
  }
}
</script>

<style>

</style>
