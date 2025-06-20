<template>
    <div class="outer-container">
        <div class="inner-container-small">
            <div>
                <Stepper :active-step="0" />
            </div>
            <h3 class="heading">
                Create a new simulation or choose a previous one.
            </h3>

            <div class="new-bar">
                <input v-model="newSimulationId" type="text" placeholder="Enter new sim ID or leave blank for random id"
                    class="input" />
                <button class="button" @click="handleNewSimulation">New</button>
            </div>

            <table class="sim-table">
                <thead>
                    <tr>
                        <th>Simulation ID</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in activeSimulations" :key="index">
                        <td>{{ item }}</td>
                        <td>
                            <RouterLink :to="`/datasource/${item}`">
                                <button class="button small">Load</button>
                            </RouterLink>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
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
    components: {
        Stepper
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.heading {
    font-size: 1.4rem;
    font-weight: 500;
    text-align: center;
    margin: 2rem 0 1rem;
    color: #cfd8dc;
}

.new-bar {
    display: flex;
    justify-content: end;
    gap: 1rem;
    margin-bottom: 2rem;
    max-width: 500px;
    width: 100%;
    justify-self: end;
}

.input {
    flex: 1;
    padding: 0.7rem 1rem;
    border-radius: 6px;
    border: none;
    font-size: 1rem;
    background-color: #ffffff10;
    color: #fff;
    outline: none;
}

.input::placeholder {
    color: #ccc;
}

.button.small {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
}

.sim-table {
    width: 100%;
    border-collapse: collapse;
    color: #fff;
}

.sim-table th,
.sim-table td {
    padding: 1rem;
    border-bottom: 1px solid #ffffff22;
    text-align: left;
}

.sim-table th {
    color: #90a4ae;
    font-weight: 600;
}

.sim-table tr:hover {
    background-color: rgba(255, 255, 255, 0.05);
}
</style>
