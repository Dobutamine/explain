<template>
  <q-page padding>
    <div class="row justify-center items-start q-ma-es">
        <div class="col-3 text-center">
          <div class="row justify-center">
              <q-btn-toggle
                class="q-mb-sm"
                color="grey-10"
                toggle-color="teal-10"
                size="sm"
                v-model="slide_left"
                :options="[
                  { label: 'files', value: 'files' },
                  { label: 'props', value: 'props' },
                  { label: 'scripts', value: 'scripts' }]"
                />
            </div>
            <q-carousel
            v-model="slide_left"
            transition-prev="slide-right"
            transition-next="slide-left"
            animated
            dark
            keep-alive
            :height="height"
          >
            <q-carousel-slide name="files">
                <FileReader></FileReader>
            </q-carousel-slide>
            <q-carousel-slide name="props">
                <ModelProps></ModelProps>
            </q-carousel-slide>
            <q-carousel-slide name="scripts">
                <ScriptEditor></ScriptEditor>
            </q-carousel-slide>
            <q-carousel-slide name="log">
                <ModelLog></ModelLog>
            </q-carousel-slide>
            </q-carousel>
          <!-- </q-scroll-area> -->
        </div>
        <div class="col text-center">
          <div class="row justify-center">
              <q-btn-toggle
                color="grey-10"
                @input="windowChanged"
                class="q-mb-sm"
                toggle-color="teal-10"
                size="sm"
                v-model="slide"
                :options="[
                  { label: 'chart1', value: 'modelchart' },
                  { label: 'chart2', value: 'modelchart2' },
                  { label: 'diagram', value: 'diagram' },
                  { label: 'ventilator', value: 'ventilator' },
                  { label: 'ecmo', value: 'ecmo' },
                  { label: 'config', value: 'json' }]"
                />
            </div>
          <!-- <q-scroll-area v-bind:style="{ height: height + 'px'}"> -->
          <q-carousel
            v-model="slide"
            transition-prev="slide-right"
            transition-next="slide-left"
            animated
            dark
            keep-alive
            :height="height"
          >
             <q-carousel-slide name="ventilator">
              <Ventilator></Ventilator>
                <Controller></Controller>
             </q-carousel-slide>
             <q-carousel-slide name="ecmo">
              <ECMO></ECMO>
                <Controller></Controller>
             </q-carousel-slide>
             <q-carousel-slide name="modelchart">
              <LightningChart chartNo="1" ></LightningChart>
                <Controller></Controller>
             </q-carousel-slide>
             <q-carousel-slide name="modelchart2">
              <LightningChart chartNo="2" ></LightningChart>
                <Controller></Controller>
             </q-carousel-slide>
             <!-- <q-carousel-slide name="vitaltrends">
              <VitalTrends></VitalTrends>
                <Controller></Controller>
             </q-carousel-slide> -->
             <q-carousel-slide name="diagram">
              <ModelDiagram></ModelDiagram>
                <Controller></Controller>
             </q-carousel-slide>
             <q-carousel-slide name="json">
              <JSONEditor></JSONEditor>
             </q-carousel-slide>
          </q-carousel>
          <!-- </q-scroll-area> -->
        </div>
        <div class="col-3 text-center">
          <div class="row justify-center">
              <q-btn-toggle
                color="grey-10"
                class="q-mb-sm"
                toggle-color="teal-10"
                size="sm"
                v-model="slide_right"
                :options="[
                { label: 'numbers', value: 'bignumbers' },
                  { label: 'monitoring', value: 'monitor' },
                  { label: 'editor', value: 'editor' }
                  ]"
                />
            </div>
            <q-carousel
            v-model="slide_right"
            transition-prev="slide-right"
            transition-next="slide-left"
            animated
            dark
            keep-alive
            :height="height"
            >
            <q-carousel-slide name="editor">
            <DiagramBuilder></DiagramBuilder>
            </q-carousel-slide>
            <q-carousel-slide name="monitor">
            <PatientMonitor></PatientMonitor>
            <Log></Log>
            </q-carousel-slide>
            <q-carousel-slide name="intellivue">
            <Intellivue></Intellivue>
            </q-carousel-slide>
            <q-carousel-slide name="bignumbers">
            <BigNumbers></BigNumbers>
            </q-carousel-slide>
            </q-carousel>
        </div>
    </div>
  </q-page>
</template>

<script>

import LightningChart from 'components/LightningChart'
import Controller from 'components/Controller'
import FileReader from 'components/FileReader'
import ModelDiagram from 'components/Diagram'
import ScriptEditor from 'components/ScriptEditor'
import DiagramBuilder from 'components/DiagramBuilder'
import ModelProps from 'components/PropertyEditor'
import PatientMonitor from 'components/Monitoring'
import Intellivue from 'components/Intellivue'
// import VitalTrends from 'components/VitalTrends'
import Ventilator from 'components/VentilatorController'
import JSONEditor from 'components/JSONEditor'
import ECMO from 'components/ECMO'
import BigNumbers from 'components/BigNumbers'
import Log from 'components/Log'

export default {
  name: 'PageIndex',
  components: {
    LightningChart,
    Controller,
    FileReader,
    ModelDiagram,
    DiagramBuilder,
    ScriptEditor,
    ModelProps,
    PatientMonitor,
    Intellivue,
    Ventilator,
    JSONEditor,
    BigNumbers,
    ECMO,
    Log
  },
  data () {
    return {
      height: '2024px',
      slide: 'modelchart',
      slide_left: 'props',
      slide_right: 'monitor'
    }
  },
  mounted () {
    // attach an event handler to the model instance
    this.height = (this.$q.screen.height - 100) + 'px'
    this.max_width = this.$q.screen.width
    this.$q.dark.set(true)
  },
  beforeDestroy () {
    // remove the event handler from memory
    delete this.modelEventListener
  },
  methods: {
    windowChanged () {
      if (this.slide === 'ventilator') {
        this.$root.$emit('show_ventilator')
      }
    }

  }
}
</script>
