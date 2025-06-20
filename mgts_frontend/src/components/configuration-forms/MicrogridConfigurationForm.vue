<template>
    <div class="outer-box">
        <div class="microgrid-stat-box">
            <div class="mg-properties">
                <div class="related-properties">
                    <label>
                        Charge efficiency
                    </label>
                    <input type="number" v-model.number="localMicroGridData.chargeEfficiency"></input>

                    <label>
                        Discharge efficiency
                    </label>
                    <input type="number" v-model.number="localMicroGridData.dischargeEfficiency"></input>
                </div>

                <div class="related-properties">
                    <label>
                        Initial stored
                    </label>
                    <input type="number" v-model.number="localMicroGridData.initialStored"></input>

                    <label>
                        Max stored
                    </label>
                    <input type="number" v-model.number="localMicroGridData.maxStored"></input>
                </div>
            </div>

            <div class="related-properties">
            <label>
                Initial Role
            </label>
            <select v-model="localMicroGridData.initialRole">
                <option>Hawk</option>
                <option>Dove</option>
            </select>
            </div>
        </div>

        <div class="measurement-box">
            <table border="1">
                <thead>
                    <tr>
                        <th></th>
                        <th v-for="time in simulationDuration">
                            {{ time - 1 }}
                        </th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>
                            Production
                        </td>
                        <td v-for="time in simulationDuration">
                            <input class="small-input" type="number"
                                v-model.number="localMicroGridData.production[time - 1]"></input>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            Consumption
                        </td>
                        <td v-for="time in simulationDuration">
                            <input class="small-input" type="number"
                                v-model.number="localMicroGridData.consumption[time - 1]"></input>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
export default {
    name: 'MicrogridConfigurationForm',
    data() {
        return {
            localMicroGridData: {
                ...this.microGrid
            }
        }
    },
    props: {
        simulationDuration: {
            type: Number,
            default: 5
        },
        microGrid: {
            type: Object
        }
    },
    emits: ['update:microGrid'],
    watch: {
        localMicroGridData: {
            handler(newVal) {
                this.$emit('update:microGrid', { ...newVal })
            },
            deep: true
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

.outer-box {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    padding: 2rem;
    border-radius: 1rem;
    background: rgba(255, 255, 255, 0.05);
    box-shadow: 0 0 12px rgba(0, 0, 0, 0.3);
    font-family: 'Inter', sans-serif;
    color: #e0f7fa;
}

/*
@media (min-width: 768px) {
  .outer-box {
    flex-direction: row;
    justify-content: space-between;
  }
}
  */

.microgrid-stat-box {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 250px;
    flex-shrink: 0;
}

.microgrid-stat-box label {
    font-weight: 600;
    font-size: 0.95rem;
    color: #80deea;
}

.microgrid-stat-box input,
.microgrid-stat-box select {
    background-color: #37474f;
    border: none;
    border-radius: 6px;
    padding: 0.4rem 0.6rem;
    color: white;
    font-size: 1rem;
    transition: all 0.2s ease;
}

.microgrid-stat-box input:focus,
.microgrid-stat-box select:focus {
    outline: none;
    background-color: #455a64;
}

.measurement-box {
    overflow-x: auto;
    background-color: rgba(255, 255, 255, 0.03);
    border-radius: 10px;
    padding: 1rem;
    flex-grow: 1;
}

table {
    border-collapse: collapse;
    width: 100%;
    color: #fff;
    font-size: 0.95rem;
}

th,
td {
    padding: 0.5rem;
    text-align: center;
    border: 1px solid #607d8b;
}

th {
    background-color: #263238;
    font-weight: 600;
}

td:first-child {
    font-weight: 600;
    background-color: #37474f;
    color: #b2ebf2;
}

.small-input {
    width: 60px;
    padding: 0.25rem;
    background-color: #455a64;
    color: white;
    border: none;
    border-radius: 4px;
}

.small-input:focus {
    outline: none;
    background-color: #546e7a;
}

.mg-properties {
    display: flex;
    flex-direction: row;
    gap:1rem;
}

.related-properties {
    display: flex;
    flex-direction: column;
    max-width: 200px;
}
</style>