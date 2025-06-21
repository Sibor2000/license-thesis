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

        <div class="table-box">
            <table border="1" class="param-table">
                <thead>
                    <tr>
                        <th class="param-table-cell param-table-header"></th>
                        <th v-for="time in simulationDuration" class="param-table-cell param-table-header">
                            {{ time - 1 }}
                        </th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td class="param-table-cell param-table-label">
                            Production
                        </td>
                        <td v-for="time in simulationDuration" class="param-table-cell">
                            <input class="small-input" type="number"
                                v-model.number="localMicroGridData.production[time - 1]"></input>
                        </td>
                    </tr>
                    <tr>
                        <td class="param-table-cell param-table-label">
                            Consumption
                        </td>
                        <td v-for="time in simulationDuration" class="param-table-cell">
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