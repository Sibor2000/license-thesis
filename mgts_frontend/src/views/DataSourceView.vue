<template>
    <div class="outer-container">
        <Stepper :active-step="1" />

        <div>
            <h3>
                Adjust the parameters for the simulation and the optimizer.
            </h3>
            <h3>
                Upload your own, pick one from the example scenarios or build your own.
            </h3>
        </div>

        <div class="config-zone">
            <div class="nav-button-row">
                <RouterLink to="/select_simulation" class="nav-button">
                    <button>
                        Back to simulation selection
                    </button>
                </RouterLink>
                <button @click="submitAndRedirect">
                    Set & Next
                </button>
            </div>

            <div class="inner-container">
                <div class="config-option">
                    <input type="file" accept=".json" @change="handleFileUpload" />
                </div>
                <div class="config-option">
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

            <div v-if="activeOption" class="active-option">
                Active option: {{ activeOption }}
            </div>

            <div class="param-zone">
                <h4>Adjust parameters</h4>
                <div class="button-row">
                    <div>
                        <button @click="activeTab = -1">
                            Simulation parameters
                        </button>
                    </div>
                    <div v-for="index in nrOfMicrogrids">
                        <button @click="activeTab = index - 1">
                            {{ microGridArray?.[index - 1]?.id }}
                        </button>
                    </div>
                </div>

                <div :key="dataSourceKey">
                    <SimulationConfigurationForm v-if="activeTab === -1" v-model:simulationDuration="simulationDuration"
                        v-model:nrOfMicrogrids="nrOfMicrogrids" v-model:sellThreshold="sellThreshold"
                        v-model:buyThreshold="buyThreshold" v-model:eMax="eMax" />
                    <div v-for="index in nrOfMicrogrids">
                        <MicrogridConfigurationForm v-if="activeTab == index - 1"
                            :simulation-duration="simulationDuration" v-model:micro-grid="microGridArray[index - 1]" />
                    </div>
                </div>
            </div>

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
import Stepper from '@/components/Stepper.vue'
import api from '@/services/api'

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
            eMax: 0,
            dataSourceKey: 0,
        }
    },
    mounted() {
        this.loadExampleConfigs()
        this.loadCurrentSimulationParams()
    },
    methods: {
        handleFileUpload(event) {
            this.selectedFile = event.target.files[0]

            if (!this.selectedFile) {
                return
            }

            const reader = new FileReader()
            reader.onload = (e) => {
                try {
                    const parsed = JSON.parse(e.target.result)
                    this.placeScenarioObject(parsed)
                    this.activeOption = "File upload"
                } catch (error) {
                    console.log("Json parse error")
                }
            }

            reader.readAsText(this.selectedFile)
        },
        async handleExampleScenarioPick(event) {
            const response = await api.get(`/example_scenario/${this.selectedExampleConfig}`)

            this.placeScenarioObject(response.data)
            this.activeOption = this.selectedExampleConfig
        },
        placeScenarioObject(scenario) {
            try {
                this.simulationDuration = scenario.simulationDuration
                this.microGridArray = scenario.microgrids
                this.nrOfMicrogrids = scenario.nrOfMicrogrids
                this.buyThreshold = Number(scenario.buyThreshold)
                this.sellThreshold = Number(scenario.sellThreshold)
                this.eMax = Number(scenario.eMax)
                this.dataSourceKey += 1
            } catch (error) {
                console.log("Cannot parse scenario")
            }
        },
        loadMicroGrids(mgArray) {
            this.microGridArray = mgArray
        },
        async loadExampleConfigs() {
            const response = await api.get('/example_scenario_ids')
            this.exampleConfigs = response.data
        },
        async loadCurrentSimulationParams() {
            const response = await api.get(`/simulation/${this.$route.params.id}/params/json`)

            if (response.data === null) {
                return
            }

            this.placeScenarioObject(response.data)
            this.activeOption = "Previous state"
        },
        async compileSimulationData() {
            const simulationData = {
                id: this.$route.params.id,
                sellThreshold: this.sellThreshold,
                buyThreshold: this.buyThreshold,
                simulationDuration: this.simulationDuration,
                nrOfMicrogrids: this.nrOfMicrogrids,
                eMax: this.eMax,
                microgrids: this.microGridArray
            }
            console.log(simulationData)
        },
        async submitAndRedirect() {

            const simulationId = this.$route.params.id

            const simulationData = {
                id: simulationId,
                sellThreshold: this.sellThreshold,
                buyThreshold: this.buyThreshold,
                simulationDuration: this.simulationDuration,
                nrOfMicrogrids: this.nrOfMicrogrids,
                eMax: this.eMax,
                microgrids: this.microGridArray
            }

            try {
                const response = await api.post('/create_simulation', simulationData)

                if (response.status === 200) {
                    this.$router.push(`/simulation/${simulationId}`)
                }

            } catch (error) {
                console.log(error)
            }
        }
    },
    components: {
        MicrogridConfigurationForm,
        SimulationConfigurationForm,
        Stepper
    },
    watch: {
        nrOfMicrogrids(newVal, oldVal) {
            while (newVal > this.microGridArray.length) {
                this.microGridArray.push({
                    id: this.microGridArray.length,
                    production: [],
                    consumption: []
                })
            }
        }
    },
    props: ['id']
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
    max-height: 20px;
}

.outer-container {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    height: 50vh;
    margin: 15vh;
    gap: 50px
}

.next-button {
    justify-self: right;
}

.config-option {
    width: 50%;
    height: 100%;
    display: flex;
    justify-content: center;
}

.param-zone {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background-color: darkslategray;
}

.button-row {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
}

.nav-button-row {
    display: flex;
    flex-direction: row;
    justify-content: end;
    width: 80%;
    gap: 10px;
}

.nav-button {
    align-self: flex-end;
}

.config-zone {
    width: 100%;
    height: 100%;
}

.active-option {
    text-align: center;
}
</style>