<template>
<q-card class="q-pb-sm q-pt-es q-ma-sm" bordered>
        <div v-if="isEnabled" class="row q-mt-es q-ml-md q-mr-md q-mb-sm">
    <q-select :options="stateNames" dense class="col q-mr-sm" v-model="selectedState" @input="selectState" label="select chart layout" style="width: 100px; font-size: 12px"></q-select>
    <q-btn class="q-ma-xs" dense color="negative" size="sm"  @click="deleteState">
      <q-icon name="delete"></q-icon>
    </q-btn>
    <q-btn class="q-ma-xs" dense color="teal-7" size="sm"  @click="storeState">
      <q-icon name="bookmark"></q-icon>
    </q-btn>
    <q-btn class="q-ma-xs" dense color="teal-7" size="sm" @click="screenshot">
      <q-icon name="screenshot"></q-icon>
    </q-btn>
    <q-btn class="q-ma-xs" dense color="teal-7" size="sm" @click="exportData">
      <q-icon name="save"></q-icon>
    </q-btn>
  </div>
  <div :class="graphClass" :id="id"></div>

   <q-dialog v-model="showPopUp" position="top" auto-close>
        <q-card style="width: 350px">
          <q-card-section class="row items-center no-wrap">
            <div>
              <div class="text-weight-bold">{{ popUpMessage }}</div>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

  <div v-if="isEnabled" class="row q-mt-sm">
    <div class="col">
      <div class="q-gutter-es row gutter">
        <q-select label-color="white" v-model="xAxisModel" :options="xAxisModels" hide-bottom-space filled dense square @input="xAxisChanged" label="x model" style="width: 100px; font-size: 12px" />
        <q-select label-color="white" v-model="xAxisProp" :options="xAxisProps" hide-bottom-space filled dense square label="property" style="width: 100px; font-size: 12px" />
      </div>
    </div>
    <div class="col">
      <div class="q-gutter-es row gutter">
        <q-select label-color="red-6" v-model="chartCh1Model"  :options="channel1Models" hide-bottom-space filled dense square @input="ch1Changed" label="y1 model" style="width: 100px; font-size: 12px" />
        <q-select label-color="red-6" v-model="chartCh1Prop" :options="channel1Props" hide-bottom-space filled dense square label="property" style="width: 100px; font-size: 12px" />
      </div>
    </div>
    <div class="col">
      <div class="q-gutter-es row gutter">
        <q-select label-color="light-green-13" v-model="chartCh2Model" :options="channel2Models" hide-bottom-space filled dense square @input="ch2Changed" label="y2 model" style="width: 100px; font-size: 12px"/>
        <q-select label-color="light-green-13" v-model="chartCh2Prop" :options="channel2Props" hide-bottom-space filled dense square label="property" style="width: 100px; font-size: 12px"/>
      </div>
    </div>
  </div>

  <div v-if="showSummary" class="row q-mt-sm">
    <div class="col">
      <div class="q-gutter-es row gutter">
        <q-input label-color="white" v-model="xMin" filled dense square label="minimum" style="width: 100px; font-size: 12px" />
        <q-input label-color="white" v-model="xMax" filled dense square label="maximum" style="width: 100px; font-size: 12px" />
      </div>
      <div class="q-gutter-es row gutter">
        <q-input label-color="white" v-model="xMean" filled dense square label="mean" style="width: 100px; font-size: 12px" />
        <q-input label-color="white" v-model="xSD" filled dense square label="sd" style="width: 100px; font-size: 12px" />
      </div>
      <div class="q-gutter-es row gutter">
        <q-input label-color="white" v-model="xPerMinute" filled dense square label="/min" style="width: 100px; font-size: 12px" />
        <q-input label-color="white" v-model="xPerBeat" filled dense square label="/beat" style="width: 100px; font-size: 12px" />
      </div>
    </div>
    <div class="col">
      <div class="q-gutter-es row gutter">
        <q-input label-color="red-6" v-model="y1Min" filled dense square label="minimum" style="width: 100px; font-size: 12px" />
        <q-input label-color="red-6" v-model="y1Max" filled dense square label="maximum" style="width: 100px; font-size: 12px" />
      </div>
      <div class="q-gutter-es row gutter">
        <q-input label-color="red-6" v-model="y1Mean" filled dense square label="mean" style="width: 100px; font-size: 12px" />
        <q-input label-color="red-6" v-model="y1SD" filled dense square label="sd" style="width: 100px; font-size: 12px" />
      </div>
      <div class="q-gutter-es row gutter">
        <q-input label-color="red-6" v-model="y1PerMinute" filled dense square label="/min" style="width: 100px; font-size: 12px" />
        <q-input label-color="red-6" v-model="y1PerBeat" filled dense square label="/beat" style="width: 100px; font-size: 12px" />
      </div>
    </div>
    <div class="col">
      <div class="q-gutter-es row gutter">
        <q-input label-color="light-green-13" v-model="y2Min" filled dense square label="minimum" style="width: 100px; font-size: 12px" />
        <q-input label-color="light-green-13" v-model="y2Max" filled dense square label="maximum" style="width: 100px; font-size: 12px" />
      </div>
      <div class="q-gutter-es row gutter">
        <q-input label-color="light-green-13" v-model="y2Mean" filled dense square label="mean" style="width: 100px; font-size: 12px" />
        <q-input label-color="light-green-13" v-model="y2SD" filled dense square label="sd" style="width: 100px; font-size: 12px" />
      </div>
      <div class="q-gutter-es row gutter">
        <q-input label-color="light-green-13" v-model="y2PerMinute" filled dense square label="/min" style="width: 100px; font-size: 12px" />
        <q-input label-color="light-green-13" v-model="y2PerBeat" filled dense square label="/beat" style="width: 100px; font-size: 12px" />
      </div>
    </div>
  </div>

  <div v-if="isEnabled" class="q-gutter-lg row gutter q-ma-xs">
    <q-checkbox v-model="showSummary" dense label="summary" style="font-size: 12px"/>
    <q-checkbox v-model="autoScale" dense label="autoscale" @input="autoScaleToggle" style="font-size: 12px"/>
    <q-input v-if="!autoScale" v-model.number="minY" type="number" @input="autoScaleToggle" label="min" filled dense hide-bottom-space style="width: 100px; font-size: 12px"/>
    <q-input v-if="!autoScale" v-model.number="maxY" type="number" @input="autoScaleToggle"  label="max" filled dense hide-bottom-space style="width: 100px; font-size: 12px"/>
    <q-checkbox v-model="hires" dense label="hi-res" @input="hiresToggle" style="font-size: 12px"/>
    <q-checkbox v-model="scaling" dense label="multipliers" @input="channelFactoringToggle" style="font-size: 12px"/>
    <q-input v-if="scaling" v-model.number="chartCh1Factor" type="number" label="y1" filled dense style="width: 75px; font-size: 10px"/>
    <q-input v-if="scaling" v-model.number="chartCh2Factor" type="number" label="y2" filled dense style="width: 75px; font-size: 10px"/>
    <q-input v-model.number="rtFrame" type="number" label="frame(s)" filled dense style="width: 75px; font-size: 10px"/>
  </div>
<q-resize-observer @resize="onResize" />

</q-card>
</template>

<script>
import {
  lightningChart, Themes, EmptyFill, AxisScrollStrategies, AxisTickStrategies, ColorRGBA, SolidFill
} from '@arction/lcjs'

import * as Stat from 'simple-statistics'

export default {
  props: {
    chartNo: {
      required: true,
      type: String
    }
  },
  data () {
    return {
      id: 'chart',
      graphClass: 'rectangle',
      label: 'filename',
      box: false,
      isEnabled: true,
      showSummary: false,
      chart: null,
      autoScale: true,
      minY: 0,
      maxY: 100,
      exportFileName: 'chart_data',
      xAxisModel: 'time',
      xAxisProp: 'none',
      xAxisModels: [],
      xAxisProps: [],
      scaling: false,
      hires: false,
      rtFrame: 3,
      chartXAxis: null,
      chartYAxis: null,
      chartCh1Lineseries: null,
      chartCh1Data: [],
      chartCh1Model: 'LV',
      chartCh1Prop: 'pres',
      chartCh1Factor: 1,
      chartCh2Lineseries: null,
      chartCh2Data: [],
      chartCh2Model: 'AA',
      chartCh2Prop: 'pres',
      chartCh2Factor: 1,
      callback: () => {},
      callback_datalogger: this.drawGraph,
      callback_props: this.processProps,
      callback_rt: this.drawRTGraph,
      modelEventListener: null,
      datalogger_data: null,
      rt_data: null,
      snapshot: null,
      properties: null,
      selectedChannel: 1,
      channel1Models: [],
      channel1Props: [],
      channel2Models: [],
      channel2Props: [],
      channel3Models: [],
      channel3Props: [],
      xMin: 0,
      xMax: 0,
      xMean: 0,
      xSD: 0,
      xPerMinute: 0,
      xPerBeat: 0,
      y1Min: 0,
      y1Max: 0,
      y1Mean: 0,
      y1SD: 0,
      y1PerMinute: 0,
      y1PerBeat: 0,
      y2Min: 0,
      y2Max: 0,
      y2Mean: 0,
      y2SD: 0,
      y2PerMinute: 0,
      y2PerBeat: 0,
      stateName: 'test',
      stateNames: [],
      chart_states: [],
      selectedState: '',
      showPopUp: false,
      popUpMessage: 'test'
    }
  },
  methods: {
    onResize (size) {
      if (this.chart) {
        this.chart.engine.renderFrame(size.width, 250)
      }
    },
    screenshot () {
      this.chart.saveToFile('screenshot')
    },
    selectState () {
      this.chart_states.forEach(state => {
        if (state.name === this.selectedState) {
          this.xAxisModel = state.xAxisModel
          this.xAxisProp = state.xAxisProp
          this.chartCh1Model = state.chartCh1Model
          this.chartCh1Prop = state.chartCh1Prop
          this.chartCh2Model = state.chartCh2Model
          this.chartCh2Prop = state.chartCh2Prop
          this.autoScale = state.autoScale
          this.minY = state.minY
          this.maxY = state.maxY
          this.hires = state.hires
          this.showSummary = state.showSummary
          this.rtFrame = state.rtFrame
          this.scaling = state.scaling
          this.chartCh1Factor = state.chartCh1Factor
          this.chartCh2Factor = state.chartCh2Factor

          this.hiresToggle()
          this.autoScaleToggle()
          this.channelFactoringToggle()
          this.xAxisChanged()
          this.ch1Changed()
          this.ch2Changed()
        }
      })
    },
    deleteState () {
      const foundIndex = this.chart_states.findIndex(element => element.name === this.selectedState)
      const foundIndex2 = this.stateNames.findIndex(element => element === this.selectedState)

      if (foundIndex > -1) {
        // it is a new one
        this.chart_states.splice(foundIndex, 1)
        this.stateNames.splice(foundIndex2, 1)
        this.updateLocalStorageChartStates()
        this.stateName = ''
        this.selectedState = ''
        this.showPopUp = true
      }
    },
    storeState () {
      if (this.xAxisModel === 'time') {
        this.stateName = 'time vs ' + this.chartCh1Model + '_' + this.chartCh1Prop
        if (this.chartCh2Model !== 'none') {
          this.stateName += ' & ' + this.chartCh2Model + '_' + this.chartCh2Prop
        }
      } else {
        this.stateName = this.xAxisModel + '_' + this.xAxisProp + ' vs ' + this.chartCh1Model + '_' + this.chartCh1Prop
        if (this.chartCh2Model !== 'none') {
          this.stateName += ' & ' + this.chartCh2Model + '_' + this.chartCh2Prop
        }
      }

      if (this.stateName !== '') {
        const newState = {
          name: this.stateName,
          xAxisModel: this.xAxisModel,
          xAxisProp: this.xAxisProp,
          chartCh1Model: this.chartCh1Model,
          chartCh1Prop: this.chartCh1Prop,
          chartCh2Model: this.chartCh2Model,
          chartCh2Prop: this.chartCh2Prop,
          autoScale: this.autoScale,
          minY: this.minY,
          maxY: this.maxY,
          hires: this.hires,
          showSummary: this.showSummary,
          rtFrame: this.rtFrame,
          scaling: this.scaling,
          chartCh1Factor: this.chartCh1Factor,
          chartCh2Factor: this.chartCh2Factor
        }

        const foundIndex = this.chart_states.findIndex(element => element.name === this.stateName)

        if (foundIndex === -1) {
        // it is a new one
          this.chart_states.push(newState)
          this.stateNames.push(newState.name)
        } else {
          // update the old one
          this.chart_states.splice(foundIndex, 1, newState)
        }
        this.showPopUp = true
        this.selectedState = newState.name
        this.updateLocalStorageChartStates()
      } else {
        this.showPopUp = true
        this.popUpMessage = 'please provide a diagram name'
      }
    },
    updateLocalStorageChartStates () {
      this.popUpMessage = 'chart layouts updated'
      localStorage.chart_states = JSON.stringify(this.chart_states)
    },
    loadChartStatesFromLocalStorage () {
      // clear the diagram list
      this.chart_states = []
      // fill the scriptlist with an array of scripts
      if (localStorage.chart_states) {
        this.chart_states = JSON.parse(localStorage.chart_states)
      }
      // update the scriptlist names array
      this.updateChartStatesNames()
    },
    updateChartStatesNames () {
      this.stateNames = []
      this.selectedState = ''
      this.chart_states.forEach(state => {
        this.stateNames.push(state.name)
      })
    },
    exportData () {
      // download to local disk
      this.exportFileName = 'data'
      const data = JSON.stringify(this.chartCh1Data)
      const blob = new Blob([data], { type: 'text/json' })
      const e = document.createEvent('MouseEvents')
      const a = document.createElement('a')
      if (this.exportFileName.includes('.json')) {
        a.download = this.exportFileName + '-y1'
      } else {
        a.download = this.exportFileName + '-y1.json'
      }
      a.href = window.URL.createObjectURL(blob)
      a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
      e.initEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
      a.dispatchEvent(e)

      if (this.chartCh2Model !== 'none') {
        const data2 = JSON.stringify(this.chartCh2Data)
        const blob = new Blob([data2], { type: 'text/json' })
        const e = document.createEvent('MouseEvents')
        const a = document.createElement('a')
        if (this.exportFileName.includes('.json')) {
          a.download = this.exportFileName + '-y2'
        } else {
          a.download = this.exportFileName + '-y2.json'
        }
        a.href = window.URL.createObjectURL(blob)
        a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
        e.initEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
        a.dispatchEvent(e)
      }
    },
    toggleIsEnabled () {
      this.isEnabled = !this.isEnabled
      if (this.isEnabled) {
        this.graphClass = 'rectangle'
      } else {
        this.graphClass = 'rectangleHide'
      }
    },
    hiresToggle () {
      if (this.hires) {
        this.$model.setDataloggerInterval(0.005)
        this.$root.$emit('hires_on')
      } else {
        this.$model.setDataloggerInterval(0.015)
        this.$root.$emit('hires_off')
      }
    },
    autoScaleToggle () {
      if (!this.autoScale) {
        this.chartYAxis.setScrollStrategy(AxisScrollStrategies.Numeric)
        this.chartYAxis.setInterval(this.minY, this.maxY)
      } else {
        this.chartYAxis.setScrollStrategy(AxisScrollStrategies.fitting)
      }
    },
    channelFactoringToggle () {
      if (!this.scaling) {
        this.chartCh1Factor = 1
        this.chartCh2Factor = 1
      }
    },
    setDatalogger () {
      const watchModels = []

      if (this.xAxisModel !== 'none' & this.xAxisModel !== '' & this.xAxisModel !== 'time') {
        watchModels.push(this.xAxisModel)
      }

      if (this.chartCh1Model !== 'none' & this.chartCh1Model !== '') {
        watchModels.push(this.chartCh1Model)
      }

      if (this.chartCh2Model !== 'none' & this.chartCh2Model !== '') {
        watchModels.push(this.chartCh2Model)
      }

      if (watchModels.length > 0) {
        // this.$model.setDataloggerWatchedModels(watchModels)
        // emit message to the controller
        if (this.chartNo === '1') {
          this.$root.$emit('rt_watch_chart', watchModels)
        } else {
          this.$root.$emit('rt_watch_chart2', watchModels)
        }
      }
    },
    xAxisChanged () {
      this.xAxisProps.length = 0
      if (this.xAxisModel === 'time') {
        this.xAxisProp = 'none'
      }
      if (this.xAxisModel !== 'none' & this.xAxisModel !== 'time') {
        Object.keys(this.properties[this.xAxisModel]).forEach(propName => {
          if (typeof this.properties[this.xAxisModel][propName] === 'number') {
            this.xAxisProps.push(propName)
          }
        })
      }
      this.setDatalogger()
    },
    ch1Changed () {
      this.channel1Props.length = 0
      if (this.chartCh1Model !== 'none') {
        Object.keys(this.properties[this.chartCh1Model]).forEach(propName => {
          if (typeof this.properties[this.chartCh1Model][propName] === 'number') {
            this.channel1Props.push(propName)
          }
        })
        if (typeof this.chartCh1Model !== 'undefined') {
          this.$root.$emit('show_selected_comp', this.chartCh1Model)
        }
      }
      // if (this.channel1Props.length > 0) {
      //   this.chartCh1Prop = this.channel1Props[0]
      // } else {
      //   this.chartCh1Prop = ''
      // }
      this.setDatalogger()
    },
    ch2Changed () {
      this.channel2Props.length = 0
      if (this.chartCh2Model !== 'none') {
        Object.keys(this.properties[this.chartCh2Model]).forEach(propName => {
          if (typeof this.properties[this.chartCh2Model][propName] === 'number') {
            this.channel2Props.push(propName)
          }
        })
      }
      // if (this.channel2Props.length > 0) {
      //   this.chartCh2Prop = this.channel2Props[0]
      // } else {
      //   this.chartCh2Prop = ''
      // }
      this.setDatalogger()
    },
    drawRTGraph () {
      this.chartCh1Lineseries.clear()
      this.chartCh2Lineseries.clear()

      if (this.rt_data) {
        let samples = parseInt(this.rtFrame / 0.015)
        if (this.hires) {
          samples = parseInt(this.rtFrame / 0.005)
        }

        const overrunCh1 = this.chartCh1Data.length - samples
        const overrunCh2 = this.chartCh2Data.length - samples
        if (overrunCh1 > 0) {
          this.chartCh1Data.splice(0, overrunCh1)
        }
        if (overrunCh2 > 0) {
          this.chartCh2Data.splice(0, overrunCh2)
        }

        this.rt_data.forEach(dataline => {
          let xValue = dataline[this.xAxisModel][this.xAxisProp]
          if (this.xAxisProp === 'none' | this.xAxisProp === '') {
            xValue = dataline[this.xAxisModel]
          }
          if (this.chartCh1Model !== 'none') {
            this.chartCh1Data.push({
              x: xValue,
              y: dataline[this.chartCh1Model][this.chartCh1Prop] * this.chartCh1Factor
            })
          }

          if (this.chartCh2Model !== 'none') {
            this.chartCh2Data.push({
              x: xValue,
              y: dataline[this.chartCh2Model][this.chartCh2Prop] * this.chartCh2Factor
            })
          }
        })
        // console.log(this.chartCh1Data)
        this.chartCh1Lineseries.add(this.chartCh1Data)
        this.chartCh2Lineseries.add(this.chartCh2Data)
      }
    },
    drawGraph () {
      this.chartCh1Lineseries.clear()
      this.chartCh2Lineseries.clear()

      this.chartCh1Data.length = 0
      this.chartCh2Data.length = 0

      this.datalogger_data.forEach(dataline => {
        let xValue = dataline[this.xAxisModel][this.xAxisProp]
        if (this.xAxisProp === 'none' | this.xAxisProp === '') {
          xValue = dataline[this.xAxisModel]
        }

        if (this.chartCh1Model !== 'none') {
          this.chartCh1Data.push({
            x: xValue,
            y: dataline[this.chartCh1Model][this.chartCh1Prop] * this.chartCh1Factor
          })
        }

        if (this.chartCh2Model !== 'none') {
          this.chartCh2Data.push({
            x: xValue,
            y: dataline[this.chartCh2Model][this.chartCh2Prop] * this.chartCh2Factor
          })
        }
      })
      // console.log(this.chartCh1Data)
      this.chartCh1Lineseries.add(this.chartCh1Data)
      this.chartCh2Lineseries.add(this.chartCh2Data)

      this.analyzeResults()
    },
    processProps () {
      this.xAxisModels.length = 0
      this.channel1Models.length = 0
      this.channel2Models.length = 0

      this.xAxisModels.push('time')
      this.channel1Models.push('none')
      this.channel2Models.push('none')

      Object.keys(this.properties).forEach(modelName => {
        this.xAxisModels.push(modelName)
        this.channel1Models.push(modelName)
        this.channel2Models.push(modelName)
      })

      this.xAxisChanged()
      this.ch1Changed()
      this.ch2Changed()
    },
    rebuildGraph () {
      this.buildGraph()
    },
    getProps () {
      this.$model.getProperties(null)
    },
    buildGraph () {
      this.chart = lightningChart().ChartXY({
        container: this.id,
        theme: Themes.dark,
        disableAnimations: false,
        responsive: true,
        maintainAspectRatio: false
      })
      this.chart.setTitle('')
      this.chart.setPadding({ top: 0, bottom: 0, left: 15, right: 30 })
      this.chartXAxis = this.chart.getDefaultAxisX()
      this.chartXAxis.setScrollStrategy(AxisScrollStrategies.fitting)
      this.chartXAxis.setTickStrategy(AxisTickStrategies.Numeric)
      this.chartXAxis.setTitleFillStyle(EmptyFill)
      this.chartXAxis.setTickStyle((a) => a.setMajorTickStyle((b) => b.setLabelFont((font) => font.setSize(12))))
      this.chartXAxis.setTickStyle((a) => a.setMinorTickStyle((b) => b.setLabelFont((font) => font.setSize(10))))

      this.chartYAxis = this.chart.getDefaultAxisY()
      this.chartYAxis.setScrollStrategy(AxisScrollStrategies.fitting)
      this.chartYAxis.setTitleFillStyle(EmptyFill)
      this.chartYAxis.setTickStrategy(AxisTickStrategies.Numeric)
      this.chartYAxis.setTickStyle((a) => a.setMajorTickStyle((b) => b.setLabelFont((font) => font.setSize(12))))
      this.chartYAxis.setTickStyle((a) => a.setMinorTickStyle((b) => b.setLabelFont((font) => font.setSize(10))))

      // const fillStyle = new SolidFill().setColor(ColorRGBA(200, 0, 0, 60))
      // const strokeStyle = new SolidLine().setFillStyle(fillStyle.setA(255)).setThickness(2)

      // this.chartCh1Lineseries = this.chart.addAreaSeries({ yAxis: this.chartYAxis })
      //   .setName('')
      //   .setFillStyle(fillStyle)
      //   .setStrokeStyle(strokeStyle)

      this.chartCh1Lineseries = this.chart.addLineSeries()
      this.chartCh1Lineseries.setStrokeStyle((style) => style.setThickness(2))
      this.chartCh1Lineseries.setStrokeStyle((style) => style.setFillStyle(new SolidFill({ color: ColorRGBA(200, 0, 0) })))

      this.chartCh2Lineseries = this.chart.addLineSeries()
      this.chartCh2Lineseries.setStrokeStyle((style) => style.setThickness(2))
      this.chartCh2Lineseries.setStrokeStyle((style) => style.setFillStyle(new SolidFill({ color: ColorRGBA(0, 200, 0) })))
    },
    analyzeResults () {
      const xValues = []
      const y1Values = []
      const y2Values = []
      this.xMin = '-'
      this.xMax = '-'
      this.y1Min = '-'
      this.y1Max = '-'
      this.y2Min = '-'
      this.y2Max = '-'
      let noBeats = 0
      const duration = this.datalogger_data[this.datalogger_data.length - 1].time - this.datalogger_data[0].time

      this.datalogger_data.forEach(dataline => {
        if (dataline.ncc_ventricular === 1) {
          noBeats += 1
        }
        let xValue = dataline[this.xAxisModel]
        if (this.xAxisProp !== 'none') {
          xValue = dataline[this.xAxisModel][this.xAxisProp]
        }
        if (typeof xValue === 'number') {
          xValues.push(xValue)
        }

        if (dataline[this.chartCh1Model]) {
          const y1Value = dataline[this.chartCh1Model][this.chartCh1Prop]
          if (typeof y1Value === 'number') {
            y1Values.push(y1Value)
          }
        }

        if (dataline[this.chartCh2Model]) {
          const y2Value = dataline[this.chartCh2Model][this.chartCh2Prop]
          if (typeof y2Value === 'number') {
            y2Values.push(y2Value)
          }
        }
      })
      if (xValues.length > 0) {
        this.xMin = Stat.min(xValues).toFixed(4)
        this.xMax = Stat.max(xValues).toFixed(4)
        this.xMean = Stat.mean(xValues).toFixed(4)
        this.xSD = Stat.standardDeviation(xValues).toFixed(4)
        this.xPerMinute = ((Stat.sum(xValues) / this.datalogger_data.length) * 60).toFixed(4)
        this.xPerBeat = ((Stat.sum(xValues) / this.datalogger_data.length) * 60).toFixed(4)
      }
      if (y1Values.length > 0) {
        this.y1Min = Stat.min(y1Values).toFixed(4)
        this.y1Max = Stat.max(y1Values).toFixed(4)
        this.y1Mean = Stat.mean(y1Values).toFixed(4)
        this.y1SD = Stat.standardDeviation(y1Values).toFixed(4)
        this.y1PerMinute = ((Stat.sum(y1Values) / this.datalogger_data.length) * 60).toFixed(4)
        if (noBeats > 0) {
          this.y1PerBeat = ((Stat.sum(y1Values) / this.datalogger_data.length) * duration / noBeats).toFixed(4)
        } else {
          this.y1PerBeat = '-'
        }
      }
      if (y2Values.length > 0) {
        this.y2Min = Stat.min(y2Values).toFixed(4)
        this.y2Max = Stat.max(y2Values).toFixed(4)
        this.y2Mean = Stat.mean(y2Values).toFixed(4)
        this.y2SD = Stat.standardDeviation(y2Values).toFixed(4)
        this.y2PerMinute = ((Stat.sum(y2Values) / this.datalogger_data.length) * 60).toFixed(4)
        this.y2PerBeat = ((Stat.sum(y2Values) / this.datalogger_data.length) * 60).toFixed(4)
        if (noBeats > 0) {
          this.y2PerBeat = ((Stat.sum(y2Values) / this.datalogger_data.length) * duration / noBeats).toFixed(4)
        } else {
          this.y2PerBeat = '-'
        }
      }
    },
    removeGraphFromOutside (model) {
      if (this.chartCh1Model === model) {
        this.chartCh1Model = 'none'
        this.chartCh1Prop = ''
        this.chartCh1Data = []
      }
      if (this.chartCh2Model === model) {
        this.chartCh2Model = 'none'
        this.chartCh2Prop = ''
        this.chartCh2Data = []
      }
      this.setDatalogger()
    },
    selectNewGraphFromOutside (model, graphNo) {
      let prop = ''
      if (this.properties[model].subtype === 'blood_compartment' | this.properties[model].subtype === 'gas_compartment') {
        prop = 'pres'
      }
      if (this.properties[model].subtype === 'pump' | this.properties[model].subtype === 'container') {
        prop = 'pres'
      }
      if (this.properties[model].subtype === 'blood_connector' | this.properties[model].subtype === 'gas_connector') {
        prop = 'real_flow'
      }
      if (this.properties[model].subtype === 'valve') {
        prop = 'real_flow'
      }
      if (this.properties[model].subtype === 'exchanger' | this.properties[model].subtype === 'diffusor') {
        prop = 'flux_o2'
      }
      switch (graphNo) {
        case 1:
          this.chartCh1Model = model
          this.chartCh1Prop = prop
          break
        case 2:
          this.chartCh2Model = model
          this.chartCh2Prop = prop
          break
        default:
          break
      }
      this.setDatalogger()
    }
  },
  beforeDestroy () {
    this.$root.$off('add_to_graph1')
    this.$root.$off('add_to_graph2')
    this.$root.$off('remove_from_diagram')
    delete this.modelEventListener
  },
  beforeMount () {
    this.id = 'test' + Math.floor((Math.random() * 1000) + 1)
  },
  mounted () {
    this.buildGraph()

    this.modelEventListener = this.$model.engine.addEventListener('message', (message) => {
      switch (message.data.type) {
        case 'mes':
          if (message.data.data[0] === 'ready') {
            this.callback()
          }
          break
        case 'data':
          switch (message.data.target) {
            case 'datalogger_output':
              this.datalogger_data = message.data.data
              this.callback_datalogger()
              break
            case 'state':
              this.snapshot = message.data.data
              break
            case 'props':
              this.properties = message.data.data
              this.callback_props()
              break
            default:
              break
          }
          break
        case 'rt':
          this.rt_data = message.data.data
          if (this.isEnabled) {
            this.callback_rt()
          }
          break
      }
    })
    this.$model.getProperties(null)
    this.$root.$on('add_to_graph1', (e) => { this.selectNewGraphFromOutside(e, 1) })
    this.$root.$on('add_to_graph2', (e) => { this.selectNewGraphFromOutside(e, 2) })
    this.$root.$on('remove_from_diagram', (e) => { this.removeGraphFromOutside(e) })

    if (localStorage.chart_states) {
      this.chart_states = JSON.parse(localStorage.chart_states)
    }

    this.loadChartStatesFromLocalStorage()
  }
}
</script>

<style>
.rectangle {
  display: flex;
  height: 250px;
  width: 100%;
}
.rectangleHide {
  display: none;
  height: 250px;
  width: 100%;
}
.gutter {
  display: flex;
  width: 100%;
  justify-content: center;
}
</style>
