<template>
    <div class="flex-container">
        <h1>Welcome, to MGTS!</h1>

        <div>
            <RouterLink to="/datasource">
                <button>
                    Let's Begin
                </button>
            </RouterLink>
        </div>
    </div>
</template>

<style scoped>
.flex-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  height: 50vh;
}
</style>