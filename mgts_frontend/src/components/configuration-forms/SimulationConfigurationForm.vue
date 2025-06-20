<template>
    <label>
        Sell threshold
    </label>
    <br />
    <input type="number" min="0" max="100" @input="emitUpdateSellThreshold($event.target.valueAsNumber)" :value="sellThreshold"></input>
    <br />

    <label>
        Buy threshold
    </label>
    <br />
    <input type="number" min="0" max="100" @input="emitUpdateBuyThreshold($event.target.valueAsNumber)" :value="buyThreshold"></input>
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
    <input type="number" min="0" @input="emitUpdateEMax($event.target.valueAsNumber)"  :value="eMax"></input>
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
    },
    emitUpdateSellThreshold(sellThreshold){
        if (Number.isNaN(sellThreshold)) {
            return
        }
        this.$emit('update:sellThreshold', Math.max(0, Math.min(100, sellThreshold)))
    },
    emitUpdateBuyThreshold(buyThreshold){
        if (Number.isNaN(buyThreshold)) {
            return
        }
        this.$emit('update:buyThreshold', Math.max(0,Math.min(100, buyThreshold)))
    },
    emitUpdateEMax(eMax){
        if (Number.isNaN(eMax)) {
            return
        }
        this.$emit('update:eMax', Math.max(0, eMax))
    },
}
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

:host {
  font-family: 'Inter', sans-serif;
  color: #e0f7fa;
}

label {
  display: block;
  font-weight: 600;
  color: #80deea;
  margin-top: 1rem;
  margin-bottom: 0.4rem;
  font-size: 0.95rem;
}

input[type="number"] {
  background-color: #37474f;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
  color: white;
  font-size: 1rem;
  width: 100%;
  max-width: 300px;
  transition: background-color 0.2s ease;
}

input[type="number"]:focus {
  outline: none;
  background-color: #455a64;
}

br {
  display: none;
}

</style>