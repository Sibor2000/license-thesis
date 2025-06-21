<template>
    <div class="outer-container">
        <div class="inner-container">

            <Stepper :active-step="1" />

            <div>
                <h3>
                    Adjust the parameters for the simulation and the optimizer.
                </h3>
                <h3>
                    Upload your own, pick one from the example scenarios or build your own.
                </h3>
                <h3>
                    In case of not selecting GA parameters, default ones will be selected.
                </h3>
            </div>

            <div class="nav-button-row">
                <RouterLink to="/select_simulation">
                    <button class="button">
                        Back to simulation selection
                    </button>
                </RouterLink>
                <button @click="submitAndRedirect" class="button">
                    Set & Next
                </button>
            </div>

            <div class="load-preset-container">
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

                    <button @click="handleExampleScenarioPick" class="button">
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
                        <button @click="activeTab = -2"
                            :class="['button-tertiary', { 'active-tab': activeTab === -2 }]">
                            Genetic algorithm parameters
                        </button>
                    </div>
                    <div>
                        <button @click="activeTab = -1"
                            :class="['button-tertiary', { 'active-tab': activeTab === -1 }]">
                            Simulation parameters
                        </button>
                    </div>
                    <div v-for="index in nrOfMicrogrids">
                        <button @click="activeTab = index - 1"
                            :class="['button-tertiary', { 'active-tab': activeTab === index - 1 }]">
                            {{ microGridArray?.[index - 1]?.id }}
                        </button>
                    </div>
                </div>

                <div :key="dataSourceKey">
                    <GAParamConfigurationForm v-if="activeTab === -2" v-model:ga-params="gaParamsList"/>
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
            <button @click="compileSimulationData" class="button">
                Compile
            </button>
        </div>
    </div>
</template>

<script>
import MicrogridConfigurationForm from '@/components/configuration-forms/MicrogridConfigurationForm.vue'
import SimulationConfigurationForm from '@/components/configuration-forms/SimulationConfigurationForm.vue'
import GAParamConfigurationForm from '@/components/configuration-forms/GAParamConfigurationForm.vue'
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
            activeTab: -2,
            simulationDuration: 0,
            sellThreshold: 100,
            buyThreshold: 0,
            eMax: 0,
            dataSourceKey: 0,
            gaParamsList: []
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
                this.gaParamsList = scenario?.gaParams ?? [];
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
                microgrids: this.microGridArray,
                ...(this.gaParamsList.length > 0 && { gaParams: this.gaParamsList })
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
                microgrids: this.microGridArray,
                gaParams: this.gaParamsList
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
        GAParamConfigurationForm,
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

h3 {
    font-size: 1.25rem;
    margin: 0.3rem 0;
    text-align: center;
    color: #e0f7fa;
}

.load-preset-container {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    justify-content: center;
}

.config-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
}

input[type="file"],
select {
    background-color: #37474f;
    color: #fff;
    padding: 0.5rem;
    border-radius: 6px;
    border: none;
    width: 220px;
    font-size: 1rem;
}

.nav-button-row {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    flex-wrap: wrap;
}

.param-zone {
    background-color: #263238;
    padding: 1rem;
    border-radius: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.param-zone h4 {
    margin: 0;
    color: #80deea;
    font-size: 1.1rem;
}

.active-option {
    text-align: center;
    font-weight: 500;
    color: #a7ffeb;
}


.active-tab {
    background-color: #2c7b84;
    color: #fff;
}
</style>