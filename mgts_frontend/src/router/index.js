import { createRouter, createWebHistory } from "vue-router";
import WelcomeView from "@/views/WelcomeView.vue";
import DataSourceView from "@/views/DataSourceView.vue";
import AdjustConfigView from "@/views/AdjustConfigView.vue";
import SimulationView from "@/views/SimulationView.vue";

const routes = [
    {path:'/', component: WelcomeView},
    {path: '/datasource', component: DataSourceView},
    {path: '/adjust', component: AdjustConfigView},
    {path: '/simulation', component: SimulationView}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router