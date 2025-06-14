<template>
    <div class="container">
        <div v-for="(item, index) in configurationSteps">

            <div class="step-piece">
                <div class="circle"
                :class="{
                    'completed-step': index < activeStep,
                    'future-step': index > activeStep,
                    'active-step': index === activeStep
                }"
                >
                    {{ index + 1 }}
                </div>

                <div>
                    {{ item.name }}
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Stepper',
    props: {
        activeStep: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            configurationSteps: [
                { name: 'Create/Choose Simulation' },
                { name: 'Adjust parameters' },
                { name: 'Run simulation' }
            ]
        }
    },
}
</script>

<style scoped>
.container {
    display: flex;
    flex-direction: row;
    width: 100%;
    justify-content: space-around;
    /*
    align-items: stretch;
    background-color: red;
    */
}

.step-piece {
    display: flex;
    flex-direction: row;
    width: 100%;
    justify-content: center;
    background-color: lightgray;
    color: black;
    border-radius: 9999px;
    gap: 0.5rem;
    padding-right: 10px;
}

.circle {
    width: 30px;
    height: 30px;
    line-height: 30px;
    background: lightgray;
    border-radius: 50%;
    margin: auto;
    color: black;
    text-align: center;
}

.active-step{
    background-color: green;
}

.completed-step{
    background-color: lightgreen;
}

.future-step{
    background-color: darkgrey;
}

</style>