<template>
  <q-card class="q-pb-sm q-pt-es q-ma-sm" bordered>

   <div v-if="isEnabled && !newStateEnabled" class="row q-mt-es q-ml-md q-mr-md q-mb-sm">
    <q-select :options="stateNames" class="col q-mr-sm" v-model="selectedState" @input="selectState" label="select existing diagram">
    </q-select>
  </div>

  <div v-if="isEnabled && !stateLoaded && !newStateEnabled" class="row q-ma-md">
        <q-btn dense color="teal-7" style="width: 100%" @click="buildNewState">NEW DIAGRAM</q-btn>
  </div>

  <div v-if="isEnabled && newStateEnabled" class="row q-ma-sm">
        <q-input type="text" label="new diagram name" v-model='stateName' class="col q-mr-sm" dense color="teal-7" ></q-input>
  </div>

    <div v-if="isEnabled && addEnabled" class="q-mt-sm">
      <q-separator></q-separator>
      <div class="row q-mt-sm">
          <q-select class="col" v-model="selectedModel" :options="models" @input="addToList" filled dense square label="select model to add" style="width: 100%" />
       </div>
    </div>

  <div v-if="isEnabled && addEnabled" class="row q-mt-sm">
      <q-list class="q-ma-es q-pa-sm" highlight separator style="width: 100%">
        <q-scroll-area style="height: 150px">
        <q-item v-for="(field, index) in currentModelsInDiagram" :key='index' dense v-ripple clickable @click="modelChanged(field, index)">
          <q-item-label class="text-caption q-pt-sm" style="width: 100%">
            {{ field }}
          </q-item-label>
        </q-item>
         </q-scroll-area>
      </q-list>
  </div>

 <div v-if="isEnabled && addEnabled" class="q-mt-sm">
      <div class="row q-mt-sm">
           <q-input class="col" :value="selectedCurrentModel" filled dense square label="selected model" style="width: 100%" />
      </div>
      <div class="row q-mt-sm">
           <q-toggle class="col q-ml-sm center" color="teal-7" v-model="autoSelectInGraph" size="sm" filled dense square label="show in graph and editor" style="width: 100%" />
      </div>

  </div>

  <div v-if="isEnabled && showActions" class="row q-ma-md">
    <q-separator></q-separator>
    <q-btn class="q-mt-sm q-mr-sm col" dense color="black" @click="addToGraph2" style="width: 100%" >
      <q-icon name="2k" class="text-white" style="font-size: 1rem;" />
    </q-btn>
    <q-btn class="q-mt-sm col" dense color="negative" @click="removeFromDiagram" style="width: 100%" >
        <q-icon name="delete_forever" class="text-white" style="font-size: 1rem;" />
    </q-btn>
  </div>

  <div v-if="isEnabled && addEnabled" class="q-mt-sm">
        <div class="row q-mt-sm">
          <q-input class="col" type="number"  v-model="scaling" @input="updateScale" filled dense square label="scale" style="width: 100%" />
          <q-input class="col" type="number"  v-model="speed" @input="updateSpeed" filled dense square label="speed" style="width: 100%" />
      </div>

  </div>

  <div v-if="isEnabled && addEnabled" class="row q-ma-md">
    <q-separator></q-separator>
    <q-btn class="q-mt-sm q-mr-sm col" dense color="teal-7" @click="addToDiagram" style="width: 100%" >
      <q-icon name="add_to_queue" class="text-white" style="font-size: 1rem;" />
    </q-btn>
    <q-btn class="q-mt-sm q-mr-sm col" dense color="teal-7" @click="cancelState"  style="width: 100%" >
      <q-icon name="cancel" label="cancel" class="text-white" style="font-size: 1rem;" />
    </q-btn>
    <q-btn class="q-mt-sm q-mr-sm col" dense color="teal-7" @click="storeDiagram" style="width: 100%" >
      <q-icon name="save_alt" class="text-white" style="font-size: 1rem;" />
    </q-btn>
    <q-btn class="q-mt-sm col" dense color="negative" @click="deleteState" style="width: 100%" >
        <q-icon name="delete_forever" class="text-white" style="font-size: 1rem;" />
    </q-btn>
  </div>

   <q-dialog v-model="showPopUp" position="top" auto-close>
        <q-card style="width: 350px">
          <q-card-section class="row items-center no-wrap">
            <div>
              <div class="text-weight-bold">{{ popUpMessage }}</div>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

     <q-separator></q-separator>

    <div v-if="isEnabled && addEnabled" class="row q-ma-md">
        <q-btn dense color="teal-7" style="width: 100%" @click="prepareToDownload">SAVE DIAGRAM TO DISK</q-btn>
    </div>
    <div v-if="diagramIOEnabled" class="row q-ma-md">
    <q-file
      v-model="fileToBeImported"
      dense
      label="load diagram from disk"
      filled
      @input="importDiagramList"
    >
      <q-icon name="save" class="text-grey" style="font-size: 1rem;" />
    </q-file>
    </div>
    <div>
      <q-btn @click="normalState">Normal Neonate</q-btn>
    </div>
  </q-card>
</template>

<script>
export default {
  data () {
    return {
      isEnabled: true,
      diagramIOEnabled: true,
      showActions: false,
      newStateEnabled: false,
      addEnabled: false,
      autoSelectInGraph: true,
      autoSelectInPropertyEditor: true,
      stateName: '',
      selectedState: '',
      stateNames: [],
      stateLoaded: false,
      properties: null,
      scaling: 10,
      speed: 10,
      selectedModel: '',
      models: [],
      selectedCurrentModel: '',
      diagramList: [],
      currentModelsInDiagram: [],
      layout: [],
      showPopUp: false,
      popUpMessage: '',
      fileToBeImported: null,
      normalNeonateState: {
        name: 'normal neonate',
        scaling: 10,
        speed: 10,
        currentModelsInDiagram: ['PV_LA', 'PV', 'LA', 'LA_LV', 'LV', 'LV_AA', 'AA', 'SHUNT_DA', 'AARCH', 'APC', 'SHUNT_OFO', 'RA', 'AA_AARCH', 'AARCH_AD', 'AD', 'AD_LB', 'LB', 'AD_INTESTINES', 'INTESTINES', 'AD_LIVSPLE', 'LIVSPLE', 'AD_AR', 'AR', 'AR_KIDNEYS', 'KIDNEYS', 'AARCH_UB', 'UB', 'AARCH_BRAIN', 'BRAIN', 'LB_VCIE', 'VCIE', 'KIDNEYS_VR', 'VR', 'VR_VCIE', 'LIVSPLE_VCIE', 'INTESTINES_VCIE', 'UB_VCS', 'VCS', 'BRAIN_VCS', 'VCIE_VCII', 'VCII', 'VCII_RA', 'VCS_RA', 'APC_LL', 'LL', 'APC_LR', 'LR', 'LL_PV', 'LR_PV', 'RA_RV', 'RV', 'RV_APC'],
        layout: [{ name: 'PV', xSprite: 0.6633499170812603, ySprite: 0.2591210613598673, xScale: 1, yScale: 1, rotation: 0 }, { name: 'LA', xSprite: 0.746268656716418, ySprite: 0.36276948590381425, xScale: 1, yScale: 1, rotation: 0 }, { name: 'LV', xSprite: 0.7711442786069652, ySprite: 0.4249585406301824, xScale: 1, yScale: 1, rotation: 0 }, { name: 'AA', xSprite: 0.7960199004975125, ySprite: 0.538971807628524, xScale: 1, yScale: 1, rotation: 0 }, { name: 'AARCH', xSprite: 0.7960199004975125, ySprite: 0.6322553897180763, xScale: 1, yScale: 1, rotation: 0 }, { name: 'APC', xSprite: 0.33167495854063017, ySprite: 0.2591210613598673, xScale: 1, yScale: 1, rotation: 0 }, { name: 'RA', xSprite: 0.20729684908789386, ySprite: 0.4767827529021558, xScale: 1, yScale: 1, rotation: 0 }, { name: 'AD', xSprite: 0.7545605306799337, ySprite: 0.7877280265339967, xScale: 1, yScale: 1, rotation: 0 }, { name: 'LB', xSprite: 0.4975124378109453, ySprite: 0.9535655058043117, xScale: 1, yScale: 1, rotation: 0 }, { name: 'INTESTINES', xSprite: 0.4975124378109453, ySprite: 0.8913764510779435, xScale: 1, yScale: 1, rotation: 0 }, { name: 'LIVSPLE', xSprite: 0.4975124378109453, ySprite: 0.7877280265339967, xScale: 1, yScale: 1, rotation: 0 }, { name: 'AR', xSprite: 0.6053067993366501, ySprite: 0.8291873963515753, xScale: 1, yScale: 1, rotation: 0 }, { name: 'KIDNEYS', xSprite: 0.4975124378109453, ySprite: 0.8395522388059701, xScale: 1, yScale: 1, rotation: 0 }, { name: 'UB', xSprite: 0.4892205638474295, ySprite: 0.5804311774461027, xScale: 1, yScale: 1, rotation: 0 }, { name: 'BRAIN', xSprite: 0.4892205638474295, ySprite: 0.6322553897180763, xScale: 1, yScale: 1, rotation: 0 }, { name: 'VCIE', xSprite: 0.24875621890547264, ySprite: 0.7877280265339967, xScale: 1, yScale: 1, rotation: 0 }, { name: 'VR', xSprite: 0.39800995024875624, ySprite: 0.8291873963515753, xScale: 1, yScale: 1, rotation: 0 }, { name: 'VCS', xSprite: 0.3067993366500829, ySprite: 0.6322553897180763, xScale: 1, yScale: 1, rotation: 0 }, { name: 'VCII', xSprite: 0.19900497512437812, ySprite: 0.5907960199004975, xScale: 1, yScale: 1, rotation: 0 }, { name: 'LL', xSprite: 0.4975124378109453, ySprite: 0.19693200663349916, xScale: 1, yScale: 1, rotation: 0 }, { name: 'LR', xSprite: 0.4975124378109453, ySprite: 0.2591210613598673, xScale: 1, yScale: 1, rotation: 0 }, { name: 'RV', xSprite: 0.24875621890547264, ySprite: 0.36276948590381425, xScale: 1, yScale: 1, rotation: 0 }]
      }
    }
  },
  mounted () {
    this.modelEventListener = this.$model.engine.addEventListener('message', (message) => {
      if (this.isEnabled) {
        switch (message.data.type) {
          case 'data':
            switch (message.data.target) {
              case 'datalogger_output':
                this.$model.getProperties(null)
                break
              case 'props':
                this.properties = message.data.data
                this.processModels()
                break
              default:
                break
            }
            break
        }
      }
    })

    if (localStorage.explain_diagrams) {
      this.diagramList = JSON.parse(localStorage.explain_diagrams)
    }
    // get the stored list
    this.loadDiagramsFromLocalStorage()

    // get the current model properties
    this.$model.getProperties(null)

    this.$root.$on('diagram_layout', (e) => { this.receivedLayout(e) })
    this.$root.$on('diagram_layout_for_download', (e) => { this.receivedLayoutForDownload(e) })
  },
  beforeDestroy () {
    this.$root.$off('diagram_layout')
    this.$root.$off('diagram_layout_for_download')
    delete this.modelEventListener
  },
  methods: {
    toggleIsEnabled () {
      this.isEnabled = !this.isEnabled
      if (this.isEnabled) {
        this.$model.getProperties(null)
      }
    },
    loadDiagramsFromLocalStorage () {
      // clear the diagram list
      this.diagramList = []
      // fill the scriptlist with an array of scripts
      if (localStorage.explain_diagrams) {
        this.diagramList = JSON.parse(localStorage.explain_diagrams)
      }
      // update the scriptlist names array
      this.updateDiagramsListNames()
    },
    getLayoutFromDiagram () {
      this.$root.$emit('get_layout')
    },
    updateDiagramsListNames () {
      this.stateNames = []
      this.selectedState = ''
      this.diagramList.forEach(diagram => {
        this.stateNames.push(diagram.name)
      })
    },
    buildNewState () {
      this.addEnabled = true
      this.newStateEnabled = true
      this.$root.$emit('clear_diagram')
    },
    normalState () {
      this.scaling = this.normalNeonateState.scaling
      this.speed = this.normalNeonateState.speed
      this.currentModelsInDiagram = this.normalNeonateState.currentModelsInDiagram
      this.addEnabled = true
      this.stateName = this.selectedState
      this.newStateEnabled = true
      this.layout = this.normalNeonateState.layout
      this.addToDiagram()
    },
    selectState () {
      // find selected state in the diagram list
      this.diagramList.forEach(diagram => {
        if (diagram.name === this.selectedState) {
          this.scaling = diagram.scaling
          this.speed = diagram.speed
          this.currentModelsInDiagram = diagram.currentModelsInDiagram
          this.addEnabled = true
          this.stateName = this.selectedState
          this.newStateEnabled = true
          this.layout = diagram.layout
        }
      })
    },
    clearList () {
      localStorage.explain_diagrams = []
    },
    cancelState () {
      this.selectedState = ''
      this.stateName = ''
      this.currentModelsInDiagram = []
      this.addEnabled = false
      this.newStateEnabled = false
      this.showActions = false
      this.layout = []
      this.$root.$emit('clear_diagram')
      this.fileToBeImported = null
    },
    receivedLayout (layout) {
      this.layout = layout
      this.storeState()
    },
    prepareToDownload () {
      this.$root.$emit('get_layout_for_download')
    },
    receivedLayoutForDownload (layout) {
      this.layout = layout
      const currentDiagramState = {
        name: this.stateName,
        scaling: this.scaling,
        speed: this.speed,
        currentModelsInDiagram: this.currentModelsInDiagram,
        layout: this.layout
      }
      this.downloadState(currentDiagramState)
    },
    downloadState (state) {
      // download to local disk
      const data = JSON.stringify(state)
      const blob = new Blob([data], { type: 'text/json' })
      const e = document.createEvent('MouseEvents')
      const a = document.createElement('a')
      if (this.stateName.includes('.json')) {
        a.download = this.stateName
      } else {
        a.download = this.stateName + '.json'
      }
      a.href = window.URL.createObjectURL(blob)
      a.dataset.downloadurl = ['text/json', a.download, a.href].join(':')
      e.initEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
      a.dispatchEvent(e)
    },
    storeDiagram () {
      this.getLayoutFromDiagram()
    },
    storeState () {
      if (this.stateName !== '') {
        const newState = {
          name: this.stateName,
          scaling: this.scaling,
          speed: this.speed,
          currentModelsInDiagram: this.currentModelsInDiagram,
          layout: this.layout
        }

        const foundIndex = this.diagramList.findIndex(element => element.name === this.stateName)

        if (foundIndex === -1) {
        // it is a new one
          this.diagramList.push(newState)
          this.stateNames.push(newState.name)
        } else {
          // update the old one
          this.diagramList.splice(foundIndex, 1, newState)
        }
        this.showPopUp = true
        this.updateLocalStorageDiagramList()
      } else {
        this.showPopUp = true
        this.popUpMessage = 'please provide a diagram name'
      }
    },
    importDiagramList () {
      const reader = new FileReader()

      reader.onload = (e) => {
        const loadedState = JSON.parse(e.target.result)

        // check if this state is already inn the diagramList
        const foundIndex = this.diagramList.findIndex(element => element.name === loadedState.name)

        // if not then it's a new one
        if (foundIndex === -1) {
          this.diagramList.push(loadedState)
          this.stateNames.push(loadedState.name)
          this.selectedState = this.diagramList[this.diagramList.length - 1].name
        } else {
          // replace the current one
          this.diagramList.splice(foundIndex, 1, loadedState)
          this.selectedState = this.diagramList[foundIndex].name
        }
        // select the current lopaded state
        this.selectState()
      }

      reader.readAsText(this.fileToBeImported)
    },
    updateLocalStorageDiagramList () {
      this.popUpMessage = 'diagramlist updated'
      localStorage.explain_diagrams = JSON.stringify(this.diagramList)
    },
    deleteState () {
      const foundIndex = this.diagramList.findIndex(element => element.name === this.stateName)
      const foundIndex2 = this.stateNames.findIndex(element => element === this.stateName)

      if (foundIndex > -1) {
        // it is a new one
        this.diagramList.splice(foundIndex, 1)
        this.stateNames.splice(foundIndex2, 1)
        this.updateLocalStorageDiagramList()
        this.currentModelsInDiagram = []
        this.stateName = ''

        this.showPopUp = true
      }
    },
    processModels () {
      this.models.length = 0

      Object.keys(this.properties).forEach(modelName => {
        this.models.push(modelName)
      })
    },
    modelChanged (field, index) {
      this.selectedCurrentModel = field
      this.addToGraph1()
      this.showActions = true
    },
    updateScale () {
      this.$root.$emit('update_scale', this.scaling / 10)
    },
    updateSpeed () {
      this.$root.$emit('update_speed', this.speed / 10)
    },
    addToGraph1 () {
      if (this.autoSelectInGraph) {
        this.$root.$emit('add_to_graph1', this.selectedCurrentModel)
      }
    },
    addToGraph2 () {
      this.$root.$emit('add_to_graph2', this.selectedCurrentModel)
    },
    removeFromDiagram () {
      this.$root.$emit('remove_from_diagram', this.selectedCurrentModel)
      const index = this.currentModelsInDiagram.findIndex((element) => element === this.selectedCurrentModel)
      if (index > -1) {
        this.currentModelsInDiagram.splice(index, 1)
        this.selectedCurrentModel = ''
      }
    },
    addToList () {
      if (this.selectedModel !== '') {
        const found = this.currentModelsInDiagram.includes(this.selectedModel)
        if (!found) {
          this.currentModelsInDiagram.push(this.selectedModel)
        }
        // check whether this is a connector because then we have to add in the connected compartments also
        if (this.properties[this.selectedModel].subtype === 'BloodConnector' | this.properties[this.selectedModel].subtype === 'Valve' | this.properties[this.selectedModel].subtype === 'GasConnector') {
          const compFrom = this.properties[this.selectedModel].comp_from
          const compTo = this.properties[this.selectedModel].comp_to
          if (!this.currentModelsInDiagram.includes(compFrom)) { this.currentModelsInDiagram.push(compFrom) }
          if (!this.currentModelsInDiagram.includes(compTo)) { this.currentModelsInDiagram.push(compTo) }
        }
        if (this.properties[this.selectedModel].subtype === 'Exchanger') {
          const compBlood = this.properties[this.selectedModel].comp_blood
          const compGas = this.properties[this.selectedModel].comp_gas
          if (!this.currentModelsInDiagram.includes(compBlood)) { this.currentModelsInDiagram.push(compBlood) }
          if (!this.currentModelsInDiagram.includes(compGas)) { this.currentModelsInDiagram.push(compGas) }
        }
        if (this.properties[this.selectedModel].subtype === 'Container') {
          // convert the list of compartments to an array
          const listOfComps = this.properties[this.selectedModel].comps.split(',')
          listOfComps.forEach(comp => {
            if (!this.currentModelsInDiagram.includes(comp)) {
              if (this.properties[comp].subtype === 'Container') {
                const listOfComps1 = this.properties[comp].comps.split(',')
                listOfComps1.forEach(comp1 => {
                  if (!this.currentModelsInDiagram.includes(comp1)) {
                    this.currentModelsInDiagram.push(comp1)
                  }
                })
              }
              // push the comp
              this.currentModelsInDiagram.push(comp)
            }
          })
        }
      } else {
        this.showPopUp = true
        this.popUpMessage = 'no model selected'
      }
    },
    addToDiagram () {
      this.currentModelsInDiagram.forEach(model => {
        const layoutIndex = this.layout.findIndex((layout) => layout.name === model)
        let currentLayout = {
          name: model,
          xSprite: 0.5,
          ySprite: 0.5,
          xScale: 1,
          yScale: 1,
          rotation: 0
        }
        if (layoutIndex > -1) {
          currentLayout = this.layout[layoutIndex]
        }
        const diagramComponent = {
          type: this.properties[model].subtype,
          id: model,
          label: model,
          modelComponents: [model],
          layout: currentLayout
        }

        if (diagramComponent.type === 'BloodCompartment' | diagramComponent.type === 'Pump') {
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        if (diagramComponent.type === 'GasCompartment') {
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        if (diagramComponent.type === 'BloodConnector' | diagramComponent.type === 'Valve') {
          diagramComponent.dbcFrom = this.properties[model].comp_from
          diagramComponent.dbcTo = this.properties[model].comp_to
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        if (diagramComponent.type === 'GasConnector') {
          diagramComponent.dbcFrom = this.properties[model].comp_from
          diagramComponent.dbcTo = this.properties[model].comp_to
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        if (diagramComponent.type === 'Container') {
          diagramComponent.modelComponents = this.properties[model].comps.split(',')
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        if (diagramComponent.type === 'Exchanger') {
          diagramComponent.dbcFrom = this.properties[model].comp_blood
          diagramComponent.dbcTo = this.properties[model].comp_gas
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        if (diagramComponent.type === 'Diffusor') {
          diagramComponent.dbcFrom = this.properties[model].comp1
          diagramComponent.dbcTo = this.properties[model].comp2
          this.$root.$emit('add_to_diagram', diagramComponent)
        }

        this.selectedModel = ''
      })
      this.updateScale()
      this.updateSpeed()
    }
  }

}
</script>

<style>

</style>
