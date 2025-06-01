<template>
    <h2>Run the simulation</h2>

    <div class="outer-container">

        <div class="sim-controll-button-row">
            <button @click="stepTime()">
                Step time
            </button>

            <RouterLink :to="`/datasource/${this.$route.params.id}`">
                <button>
                    Back to configuration
                </button>
            </RouterLink>

            <button>
                Restart simulation
            </button>
        </div>

        <div class="config-zone">
            <div class="button-row">
                <div>
                    <button>
                        Simulation
                    </button>
                </div>

                <div>
                    <button>
                        T0
                    </button>
                </div>

                <div>
                    <button>
                        T1
                    </button>
                </div>
            </div>

            <div>
                <img v-if="roleChart" :src="'data:image/png;base64,' + roleChart" />
                <img v-if="roleChart" :src="'data:image/png;base64,' + roleChart" />
                <img v-if="roleChart" :src="'data:image/png;base64,' + roleChart" />
            </div>
        </div>





    </div>

</template>

<script>
import axios from 'axios'

export default {
    props: ['id'],
    data() {
        return {
            socket: null,
            roleChart: null,
            simulationCharts: null,
            momentAnalysisCharts: null
        }
    },
    mounted() {
        this.socket = new WebSocket(`ws://localhost:8000/ws/simulation/${this.$route.params.id}`)

        this.socket.onopen = () => {
            console.log("WS connected")
        }

        this.socket.onmessage = (event) => {
            const msg = JSON.parse(event.data)
            if (msg.type === "chart") {
                this.roleChart = msg.data
            }
        }

        this.socket.onerror = (error) => {
            console.log("Error")
        }

        this.socket.onclose = () => {
            console.log("WS closed")
        }
    },
    beforeUnmount() {
        if (this.socket) {
            this.socket.close()
        }
    },
    methods:{
        async stepTime(){
            try {
                const response = await axios.post(`http://localhost:8000/simulation/${this.$route.params.id}/step`)

                console.log(response.data)
            } catch (error) {
                console.log(error)
            }
        }
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
}

.config-zone {
    display: flex;
    flex-direction: column;
    background-color: blueviolet;
    width: 100%;
    height: 100%;
}

.chart-zone {
    display: flex;
    background-color: pink;
    height: 100%;
    padding: 2px;
}

.button-row {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    gap: 4px;
}
</style>