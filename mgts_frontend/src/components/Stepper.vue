<template>
  <div class="stepper-container">
    <div class="stepper-track"></div>
    <div class="step-piece" v-for="(item, index) in configurationSteps" :key="index">
      <div class="circle" :class="{
        'completed-step': index < activeStep,
        'active-step': index === activeStep,
        'future-step': index > activeStep
      }">
        {{ index + 1 }}
      </div>
      <span class="label">{{ item.name }}</span>
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
        { name: 'Adjust Parameters' },
        { name: 'Run Simulation' }
      ]
    };
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

.stepper-container {
  display: flex;
  position: relative;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 1rem;
  background-color: transparent;
  font-family: 'Inter', sans-serif;
  gap: 1rem;

  justify-self: center;
  align-self: center;
  max-width: 750px;
}

.stepper-track {
  position: absolute;
  top: 50%;
  left: 5%;
  right: 5%;
  height: 4px;
  background-color: #555;
  z-index: 0;
  transform: translateY(-50%);
}

.step-piece {
  display: flex;
  flex-direction: row;
  gap: 20px;
  border-radius: 9999px;
  background-color: #04353b;
  z-index: 1;
  position: relative;
}

.circle {
  width: 40px;
  height: 40px;
  line-height: 40px;
  font-size: 1rem;
  border-radius: 50%;
  background-color: #999;
  color: #fff;
  font-weight: 600;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 0 0 transparent;
}

.label {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #ccc;
  width: 120px;
}

.active-step {
  background-color: #00e5ff;
  color: #00363a;
  box-shadow: 0 0 10px #00e5ff99;
}

.completed-step {
  background-color: #26a69a;
  box-shadow: 0 0 6px #26a69a88;
}

.future-step {
  background-color: #607d8b;
}
</style>
