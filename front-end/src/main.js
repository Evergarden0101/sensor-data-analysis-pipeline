import { createApp } from 'vue'
import App from './App.vue'
import './main.css';
import * as VueRouter from 'vue-router'
import HomePage from './pages/HomePage.vue';
import EcgPage from './pages/EcgPage.vue';
import EegMegPage from './pages/EegMegPage.vue';

createApp(App)
.use(VueRouter.createRouter({
   history: VueRouter.createWebHistory(process.env.BASE_URL),
    routes:[{
        path: '/',
        component: HomePage,
    }, {
        path: '/ecg',
        component: EcgPage,
    }, {
        path: '/eeg-meg',
        component: EegMegPage,
    },] 
}))
.mount('#app')
