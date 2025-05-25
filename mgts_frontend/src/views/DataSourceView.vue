<template>
    <h2>
        Upload/Select and adjust a scenario
    </h2>
    <div class="outer-container">
        <div class="inner-container">
            <div class="config-option">
                <input type="file" accept=".xlsx" @change="handleFileUpload" />

                <button @click="handleFileUploadPick">
                    Pick
                </button>
            </div>
            <div class="config-option" style="background-color: brown;">
                <select v-model="selectedExampleConfig">
                    <option disabled value="">--Select a config--</option>
                    <option v-for="exampleConfig in exampleConfigs">
                        {{ exampleConfig }}
                    </option>
                </select>

                <button @click="handleExampleScenarioPick">
                    Pick
                </button>
            </div>
        </div>

        <div v-if="activeOption">
            Selected option: {{ activeOption }}
        </div>

        <div class="config-zone">
            <div class="button-row">
                <div>
                    <button @click="activeTab = -1">
                        Simulation
                    </button>
                </div>
                <div v-for="index in nrOfMicrogrids">
                    <button @click="activeTab = index - 1">
                        {{ microGridArray?.[index - 1]?.id }}
                    </button>
                </div>
            </div>

            <div>
                <SimulationConfigurationForm v-if="activeTab === -1" v-model:simulationDuration="simulationDuration"
                    v-model:nrOfMicrogrids="nrOfMicrogrids" v-model:sellThreshold="sellThreshold"
                    v-model:buyThreshold="buyThreshold" v-model:eMax="eMax"/>
                <div v-for="index in nrOfMicrogrids">
                    <MicrogridConfigurationForm v-if="activeTab==index-1" :simulation-duration="simulationDuration" v-model:micro-grid="microGridArray[index-1]"/>
                </div>
            </div>
        </div>

        <div>
            <RouterLink to="/adjust">
                <button>
                    Next
                </button>
            </RouterLink>
        </div>

        <div>
            <button @click="compileSimulationData">
                Compile
            </button>
        </div>
    </div>
</template>

<script>
import MicrogridConfigurationForm from '@/components/configuration-forms/MicrogridConfigurationForm.vue'
import SimulationConfigurationForm from '@/components/configuration-forms/SimulationConfigurationForm.vue'
import axios from 'axios'

export default {
    data() {
        return {
            exampleConfigs: null,
            selectedExampleConfig: "",
            activeOption: null,
            selectedFile: null,
            tableData: null,
            microGridArray: [],
            nrOfMicrogrids: 0,
            activeTab: -1,
            simulationDuration: 0,
            sellThreshold: 100,
            buyThreshold: 0,
            eMax:0
        }
    },
    mounted() {
        //this.loadMicroGrids()

        this.loadExampleConfigs()
    },
    methods: {
        handleFileUpload(event) {
            this.selectedFile = event.target.files[0]
        },
        handleFileUploadPick(event) {
            this.activeOption = this.selectedFile.name
        },
        async handleExampleScenarioPick(event) {
            this.activeOption = this.selectedExampleConfig

            const response = await axios.get(`http://localhost:8000/example_scenario/${this.selectedExampleConfig}`)
            console.log(response.data)

            const simulation = response.data
            this.simulationDuration = simulation.duration
            this.microGridArray = simulation.microgrids
            this.nrOfMicrogrids = simulation.nrOfMicrogrids
            this.buyThreshold = Number(simulation.buyThreshold)
            this.sellThreshold = Number(simulation.sellThreshold)
            this.eMax = Number(simulation.eMax)
        },
        loadMicroGrids(mgArray) {
            this.microGridArray = mgArray
        },
        async loadExampleConfigs() {
            const response = await axios.get('http://localhost:8000/example_scenario_ids')
            this.exampleConfigs = response.data
        },
        compileSimulationData(){
            console.log(this.microGridArray)
        }
    },
    components: {
        MicrogridConfigurationForm,
        SimulationConfigurationForm
    },
    watch: {
        nrOfMicrogrids(newVal, oldVal) {
            while (newVal > this.microGridArray.length) {
                this.microGridArray.push({
                    id: this.microGridArray.length
                })
            }
        }
    }
}
</script>

<style scoped>
.inner-container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    height: 20vb;
}

.outer-container {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    height: 50vh;
    margin: 15vh;
}

.next-button {
    justify-self: right;
}

.config-option {
    background-color: darkblue;
    width: 50%;
    height: 100%;
}

.config-zone {
    display: flex;
    flex-direction: column;
    background-color: blueviolet;
    width: 100%;
    height: 100%;
}

.button-row {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
}
</style>