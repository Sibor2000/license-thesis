<template>
    <div class="outer-container">
        <div class="inner-container">
            <Stepper :active-step="2" />

            <h3>
                Run the simulation by clicking 'Step time'. Check out chart to gain insight and reset simulation to
                re-run.
            </h3>

            <h4>On every time step, all the microgrids do the following:</h4>
            <ul>
                <li>Calculate internal energy based on leftover energy, production and consumption.</li>
                <li>Engage in trade with other microgrids. Optimized by the GA.</li>
                <li>Calculate new role.</li>
            </ul>

            <div class="sim-controll-button-row">
                <RouterLink :to="`/datasource/${this.$route.params.id}`">
                    <button class="button">
                        Back to configuration
                    </button>
                </RouterLink>
            </div>

            <div class="sim-controll-button-row">
                <button @click="stepTime()" class="button">
                    Step time
                </button>

                <button @click="resetSimulation" class="button">
                    Reset simulation
                </button>
            </div>

            <div class="loader" v-if="performingStep">
            </div>

            <div v-if="wsTextMessage">
                {{ wsTextMessage }}
            </div>

            <div class="config-zone">
                <div class="button-row">
                    <div>
                        <button @click="activeTab = -1"
                        :class="['button-tertiary', { 'active-tab': activeTab === -1 }]">
                            Simulation
                        </button>
                    </div>

                    <div v-for="(_, index) in momentChartsList">
                        <button @click="activeTab = index"
                        :class="['button-tertiary', { 'active-tab': activeTab === index }]">
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
            wsTextMessage: null,
            performingStep: false
        }
    },
    mounted() {
        this.socket = new WebSocket(`ws://localhost:8000/ws/simulation/${this.$route.params.id}`)

        this.socket.onopen = () => {
            console.log("WS connected")
        }

        this.socket.onmessage = (event) => {
            const msg = JSON.parse(event.data)

            this.performingStep = false

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
                this.performingStep=true
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

h3,
h4 {
    color: #b2ebf2;
    text-align: center;
    margin: 0.5rem 0;
    font-weight: 500;
}

.sim-controll-button-row {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.sim-controll-button-row button:hover,
.button-row button:hover {
    background-color: #00acc1;
}

.config-zone {
    display: flex;
    flex-direction: column;
    background-color: #263238;
    border-radius: 12px;
    padding: 1rem;
    width: 100%;
}

.chart-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background-color: #37474f;
    border-radius: 8px;
}

.chart-column img {
    max-width: 100%;
    border-radius: 6px;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
}

ul {
    color: #b2ebf2;
    padding-left: 1.2rem;
    list-style-type: disc;
    margin: 0;
}

li {
    margin: 0.4rem 0;
}

.loader{
    border: 8px solid #f3f3f3;
    border-top: 8px solid #00d1ff;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1s linear infinite;
    margin: auto;
}

@keyframes spin{
    0% {transform: rotate(0deg);}
    100% {transform: rotate(360deg);}
}

.active-tab {
    background-color: #2c7b84;
    color: #fff;
}

</style>