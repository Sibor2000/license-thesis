<template>
    <div class="outer-box">
        <div class="microgrid-stat-box">
            <label>
                Charge efficiency
            </label>
            <input type="number" v-model.number="localMicroGridData.chargeEfficiency"></input>

            <label>
                Discharge efficiency
            </label>
            <input type="number" v-model.number="localMicroGridData.dischargeEfficiency"></input>


            <label>
                Initial stored
            </label>
            <input type="number" v-model.number="localMicroGridData.initialStored"></input>


            <label>
                Max stored
            </label>
            <input type="number" v-model.number="localMicroGridData.maxStored"></input>

            <label>
                Initial Role
            </label>
            <select>
                <option>Hawk</option>
                <option>Dove</option>
            </select>
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

<style>
.outer-box {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}

.microgrid-stat-box {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    flex-shrink: 20;
}

.measurement-box {
    display: flex;
    overflow-x: auto;
}

.small-input {
    width: 40px;
}
</style>