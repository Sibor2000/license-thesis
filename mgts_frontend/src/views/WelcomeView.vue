<template>
  <div class="container">
    <div class="content">
      <h1 class="title">⚡ Microgrid Trading System Simulator</h1>
      <h3 class="subtitle">A thesis project by <span class="highlight">Someone</span></h3>

      <RouterLink to="/select_simulation" class="start-link">
        <button class="start-button">🚀 Let's Begin</button>
      </RouterLink>
    </div>
  </div>
</template>

<script>
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
  font-family: 'Inter', sans-serif;
  color: #fff;
}

.content {
  text-align: center;
  padding: 2rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: fadeIn 1.2s ease-in-out;
}

.title {
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.2rem;
  font-weight: 400;
  color: #cfd8dc;
  margin-bottom: 2.5rem;
}

.highlight {
  color: #00e5ff;
  font-weight: 600;
}

.start-link {
  text-decoration: none;
}

.start-button {
  background-color: #00e5ff;
  color: #00363a;
  border: none;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.start-button:hover {
  background-color: #00bcd4;
  transform: scale(1.05);
}

@keyframes fadeIn {
  0% {
    transform: translateY(-30px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
