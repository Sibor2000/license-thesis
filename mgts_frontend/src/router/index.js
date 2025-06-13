import { createRouter, createWebHistory } from "vue-router";
import WelcomeView from "@/views/WelcomeView.vue";
import DataSourceView from "@/views/DataSourceView.vue";
import SimulationView from "@/views/SimulationView.vue";
import SelectSimulation from "@/views/SelectSimulation.vue";

const routes = [
    {path:'/', component: WelcomeView},
    {path: '/datasource/:id', component: DataSourceView, props: true},
    {path: '/simulation/:id', component: SimulationView, props: true},
    {path: '/select_simulation', component: SelectSimulation}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router