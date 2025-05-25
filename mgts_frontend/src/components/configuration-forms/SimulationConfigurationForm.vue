<template>
    <label>
        Sell threshold
    </label>
    <br />
    <input type="number" min="0" max="100" :value="sellThreshold"></input>
    <br />

    <label>
        Buy threshold
    </label>
    <br />
    <input type="number" min="0" max="100" :value="buyThreshold"></input>
    <br />

    <label>
        Duration
    </label>
    <br />
    <input type="number" @input="emitUpdateDuration($event.target.valueAsNumber)" :value="simulationDuration"
        min="0"></input>
    <br />

    <label>
        Number of Microgrids
    </label>
    <br />
    <input type="number" @input="emitUpdateMicrogridNumber($event.target.valueAsNumber)" :value="nrOfMicrogrids"
        min="0"></input>
    <br />

    <label>
        E Max
    </label>
    <br />
    <input type="number" min="0" :value="eMax"></input>
    <br />
</template>

<script>
export default {
    name: 'SimulationConfigurationForm',
    props: {
        simulationDuration: {
            type: Number,
        },
        nrOfMicrogrids: {
            type: Number
        },
        sellThreshold: {
            type: Number
        },
        buyThreshold: {
            type: Number
        },
        eMax: {
            type: Number
        }
    },
methods: {
    emitUpdateDuration(duration){
        if (Number.isNaN(duration)) {
            return
        }
        this.$emit('update:simulationDuration', Math.max(0, duration))
    },
    emitUpdateMicrogridNumber(nrOfMicrogrids){
        if (Number.isNaN(nrOfMicrogrids)) {
            return
        }
        this.$emit('update:nrOfMicrogrids', Math.max(0, nrOfMicrogrids))
    }
}
}
</script>