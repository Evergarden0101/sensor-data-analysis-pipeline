import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import en from 'element-plus/dist/locale/en.mjs'
import App from './App.vue'
import './main.css';
import * as VueRouter from 'vue-router'
import HomePage from './pages/HomePage.vue';
import SleepPage from './pages/SleepPage.vue';
import TreatmentPage from './pages/TreatmentPage.vue';
import BruxismPage from './pages/BruxismPage.vue';
import DataUploadPage from './pages/DataUploadPage.vue';

const app = createApp(App)
app.use(VueRouter.createRouter({
   history: VueRouter.createWebHistory(process.env.BASE_URL),
    routes:[{
        path: '/',
        component: HomePage,
    }, {
        path: '/sleep',
        component: SleepPage,
    }, {
        path: '/treatment',
        component: TreatmentPage,
    },{
        path: '/bruxism',
        component: BruxismPage,
    },{
        path: '/upload',
        component: DataUploadPage,
    },] 
}))
app.use(ElementPlus, {
    locale: en,
})
app.mount('#app')
