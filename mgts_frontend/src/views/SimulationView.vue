<template>
    <div class="outer-container">


        <Stepper :active-step="2" />

        <h3>
            Run the simulation by clicking 'Step time'. Check out chart to gain insight and reset simulation to re-run.
        </h3>

        <h4>
            On every time step, all the microgrids do the following:
            <h4>- Calculate internal energy based on leftover energy, production and consumption.</h4>
            <h4>- Engage in trade with other microgrids. Optimized by the GA.</h4>
            <h4>- Calculate new role.</h4>
        </h4>

        <div class="sim-controll-button-row">
            <RouterLink :to="`/datasource/${this.$route.params.id}`">
                <button>
                    Back to configuration
                </button>
            </RouterLink>
        </div>

        <div class="sim-controll-button-row">
            <button @click="stepTime()">
                Step time
            </button>

            <button @click="resetSimulation">
                Reset simulation
            </button>
        </div>

        <div v-if="wsTextMessage">
            {{ wsTextMessage }}
        </div>

        <div class="config-zone">
            <div class="button-row">
                <div>
                    <button @click="activeTab = -1">
                        Simulation
                    </button>
                </div>

                <div v-for="(_, index) in momentChartsList">
                    <button @click="activeTab = index">
                        {{ index }}
                    </button>
                </div>
            </div>

            <div>
                <div v-if="activeTab === -1" class="chart-column">
                    <img v-for="simChart in simulationCharts" :src="'data:image/png;base64,' + simChart" />
                </div>

                <div v-for="(momentCharts, index) in momentChartsList">
                    <div v-if="activeTab === index" class="chart-column">
                        <img v-for="momentChart in momentCharts" :src="'data:image/png;base64,' + momentChart" />
                    </div>
                </div>
            </div>
        </div>

    </div>

</template>

<script>
import Stepper from '@/components/Stepper.vue'
import axios from 'axios'

export default {
    props: ['id'],
    data() {
        return {
            socket: null,
            simulationCharts: [],
            momentChartsList: [],
            activeTab: -1,
            wsTextMessage: null
        }
    },
    mounted() {
        this.socket = new WebSocket(`ws://localhost:8000/ws/simulation/${this.$route.params.id}`)

        this.socket.onopen = () => {
            console.log("WS connected")
        }

        this.socket.onmessage = (event) => {
            const msg = JSON.parse(event.data)

            if (msg.type === "charts") {
                this.simulationCharts = msg.simCharts

                this.momentChartsList = this.momentChartsList.concat([msg.momentCharts])
            }

            if (msg.type === "text") {
                this.wsTextMessage = msg.payload
            }
        }

        this.socket.onerror = (error) => {
            console.log("Error")
        }

        this.socket.onclose = () => {
            console.log("WS closed")
        }

        this.loadCharts()
    },
    beforeUnmount() {
        if (this.socket) {
            this.socket.close()
        }
    },
    methods: {
        async stepTime() {
            try {
                const response = await axios.post(`http://localhost:8000/simulation/${this.$route.params.id}/step`)

                console.log(response.data)
            } catch (error) {
                console.log(error)
            }
        },
        async resetSimulation() {
            try {
                const response = await axios.post(`http://localhost:8000/simulation/${this.$route.params.id}/reset`)

                this.activeTab = -1
                this.simulationCharts = []
                this.momentChartsList = []
            } catch (error) {
                console.log(error)
            }
        },
        async loadCharts() {
            try {
                const response = await axios.get(`http://localhost:8000/simulation/${this.$route.params.id}/charts`)
                const data = response.data

                this.momentChartsList = data.momentChartsList
                this.simulationCharts = data.simulationCharts
            } catch (error) {
                console.log(error)
            }
        }
    },
    components: {
        Stepper
    }
}
</script>

<style scoped>
.outer-container {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
    height: 100%;
    margin: 15vh;
}

.sim-controll-button-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 75vb;
    background-color: pink;
}

.config-zone {
    display: flex;
    flex-direction: column;
    background-color: blueviolet;
    width: 100%;
    height: 100%;
}

.chart-column {
    display: flex;
    background-color: pink;
    height: 100%;
    width: 100%;
    flex-direction: column;
    align-items: center;
    padding: 2px;
    gap: 5px;
}

.button-row {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
}
</style>