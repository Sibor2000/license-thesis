<template>
    <div class="flex-container">
        <Stepper :active-step="0"/>
        <h3>
            Create a new simulation or choose a previous one.
        </h3>
        <div class="new-bar">
            <input v-model="newSimulationId" type="text" placeholder="Enter new sim id, or get a random id by default"
                size="40">

            <button @click="handleNewSimulation">New</button>
        </div>
        <table class="sim-table">
            <thead>
                <tr>
                    <th>
                        Simulation id
                    </th>
                    <th>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in this.activeSimulations" :key="index">
                    <td>{{ item }}</td>
                    <td>
                        <RouterLink :to="`/datasource/${item}`">
                            <button>Load</button>
                        </RouterLink>
                    </td>
                </tr>
            </tbody>
        </table>

    </div>
</template>

<script>
import router from '@/router';
import api from '@/services/api';
import Stepper from '@/components/Stepper.vue';

export default {
    data() {
        return {
            activeSimulations: [],
            newSimulationId: ""
        }
    },
    methods: {
        async getActiveSimulations() {
            const response = await api.get('/active_simulation_ids')

            this.activeSimulations = response.data
        },
        async handleNewSimulation() {
            const newSimulationId = this.newSimulationId || this.generateId();

            router.push(`/datasource/${newSimulationId}`)
        },
        generateId() {
            return Math.random().toString(36).substring(2, 10);
        }
    },
    mounted() {
        this.getActiveSimulations()
    },
    components:{
        Stepper
    }
}
</script>

<style scoped>
.flex-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 50vh;
    gap: 50px;
    margin: 15vh;
}

.sim-table {
    width: 50%;
    border-collapse: collapse;
}

.sim-table td,
.sim-table th {
    border: 2px solid;
    border-color: gray;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

.sim-table td:nth-child(1),
.sim-table th:nth-child(1) {
    border-right: none;
    text-align: start;
}

.sim-table td:nth-child(2),
.sim-table th:nth-child(2) {
    border-left: none;
    text-align: end;
}

.sim-table tr {
    width: 100%;
}

.new-bar {
    display: flex;
    justify-content: flex-end;
    width: 50%;
    gap: 10px;
}
</style>