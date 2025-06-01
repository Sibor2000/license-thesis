<template>
    <div class="flex-container">
        <h1>Welcome, to MGTS!</h1>

        <div>
            <RouterLink :to="`/datasource/${randomId}`">
                <button>
                    Let's Begin
                </button>
            </RouterLink>
        </div>
    </div>
</template>

<script>
export default {
    data(){
        return {
            randomId: this.generateId()
        }
    },
    methods:{
        generateId(){
            return Math.random().toString(36).substring(2, 10)
        }
    }
}

</script>

<style scoped>
.flex-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  height: 50vh;
}
</style>
