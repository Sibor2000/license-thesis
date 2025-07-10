<template>
    <div class="outer-container">
        <div class="inner-container">

            <Stepper :active-step="1" />

            <h3 class="heading">
                Adjust the parameters for the simulation and the optimizer.
                <br />
                Upload your own, pick one from the example scenarios or build your own.
                <br />
                In case of not selecting GA parameters, default ones will be selected.
            </h3>

            <div class="nav-button-row">
                <RouterLink to="/select_simulation">
                    <button class="button">
                        Back to simulation selection
                    </button>
                </RouterLink>
                <button @click="submitAndRedirect" class="button">
                    Set & Next
                </button>
                <RouterLink :to="simulationRoute" v-if="existingSimulation">
                    <button class="button">
                        Next
                    </button>
                </RouterLink>
            </div>

            <div class="load-preset-container">
                <div class="config-option">
                    <input type="file" accept=".json" @change="handleFileUpload" class="scenario-source" />
                </div>
                <div class="config-option">
                    <select v-model="selectedExampleConfig" class="scenario-source">
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

            <div v-if="invalidInputs.length != 0" class="active-option">
                Error
                <div v-for="invalidInput in invalidInputs">
                    {{ invalidInput }}
                </div>
            </div>

            <div class="param-zone">
                <h4 class="task-hint">Adjust parameters</h4>
                <div class="button-row">
                    <div>
                        <button @click="activeTab = -2" :class="['button-tertiary',
                            { 'active-tab': activeTab === -2 }]">
                            Genetic algorithm parameters
                        </button>
                    </div>
                    <div>
                        <button @click="activeTab = -1" :class="['button-tertiary',
                            { 'active-tab': activeTab === -1 }]">
                            Simulation parameters
                        </button>
                    </div>
                    <div v-for="index in nrOfMicrogrids">
                        <button @click="activeTab = index - 1" :class="['button-tertiary',
                            { 'active-tab': activeTab === index - 1 }]">
                            {{ microGridArray?.[index - 1]?.id }}
                        </button>
                    </div>
                </div>

                <div :key="dataSourceKey">
                    <GAParamConfigurationForm v-if="activeTab === -2" v-model:ga-params="gaParamsList" />
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
import { RouterLink } from 'vue-router'

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
            gaParamsList: [],
            invalidInputs: [],
            existingSimulation: false
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
                this.existingSimulation = false
                return
            }

            this.existingSimulation = true
            this.placeScenarioObject(response.data)
            this.activeOption = "Previous state"
        },
        validateInputs() {
            let validInputs = true
            this.invalidInputs = []

            if (this.sellThreshold < this.buyThreshold) {
                validInputs = false
                this.invalidInputs.push("Sell threshold should be greater or equal to buy threshold")
            }

            if (this.sellThreshold < 0 || this.sellThreshold > 100) {
                validInputs = false
                this.invalidInputs.push("Invalid sell threshold")
            }
            if (this.buyThreshold < 0 || this.buyThreshold > 100) {
                validInputs = false
                this.invalidInputs.push("Invalid buy threshold")
            }

            if (this.simulationDuration < 1) {
                validInputs = false
                this.invalidInputs.push("Duration needs to be at least 1")
            }
            if (this.nrOfMicrogrids < 1) {
                validInputs = false
                this.invalidInputs.push("At least one microgrid needed")
            }
            if (this.eMax < 0) {
                validInputs = false
                this.invalidInputs.push("Line capacity (eMax) needs to be at least 0")
            }

            if (!this.microGridArray.every(element => {
                if (element.chargeEfficiency > 1 || element.chargeEfficiency < 0) {
                    this.invalidInputs.push("Charge efficiencies needs to be between 0 and 1")
                    return false
                }

                if (element.dischargeEfficiency > 1 || element.dischargeEfficiency < 0) {
                    this.invalidInputs.push("Discharge efficiencies needs to be between 0 and 1")
                    return false
                }

                if (element.maxStored <= 0) {
                    this.invalidInputs.push("Max storage needs to be greater than 0")
                    return false
                }

                if (element.initialStored < 0 || element.initialStored > element.maxStored) {
                    this.invalidInputs.push("Initial storages needs to be between 0 and respective max storage")
                    return false
                }

                if (
                    element.consumption.length < this.simulationDuration ||
                    !element.consumption.every(measurement => measurement != null && measurement !== '') ||
                    element.production.length < this.simulationDuration ||
                    !element.production.every(measurement => measurement != null && measurement !== '')
                ) {
                    this.invalidInputs.push("All measurements need to be filled")
                    return false
                }

                if (
                    !element.consumption.every(measurement => measurement >= 0) ||
                    !element.production.every(measurement => measurement >= 0)
                ) {
                    this.invalidInputs.push("All measurements need to greater or equal to 0")
                    return false
                }

                return true
            })) {
                validInputs = false
            }

            if (!this.gaParamsList.every(element => {
                if (element.id == null || element.id === '') {
                    this.invalidInputs.push("GA param id can't be empty")
                    return false
                }

                if (element.pop_size < 20) {
                    this.invalidInputs.push("pop_size needs to be atleast 20")
                    return false
                }

                if (element.pc < 0 || element.pc > 1) {
                    this.invalidInputs.push("pc needs to be between 0 and 1")
                    return false
                }

                if (element.pm < 0 || element.pm > 1) {
                    this.invalidInputs.push("pm needs to be between 0 and 1")
                    return false
                }

                if (element.epoch < 5) {
                    this.invalidInputs.push("At least 5 epochs are needed")
                    return false
                }

            })) {
                validInputs = false
            }

            return validInputs
        },
        async compileSimulationData() {

            if (!this.validateInputs()) {
                return
            }

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
    props: ['id'],
    computed: {
        simulationRoute() {
            return "/simulation/" + this.$route.params.id
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

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

.scenario-source {
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
    color: #dbe4e2;
}

.task-hint {
    font-size: 1.25rem;
    margin: 0.3rem 0;
    color: #e0f7fa;
}
</style>