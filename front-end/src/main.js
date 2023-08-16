import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import en from 'element-plus/dist/locale/en.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import './main.css';
import * as VueRouter from 'vue-router'
import HomePage from './pages/HomePage.vue';
import SleepPage from './pages/SleepPage.vue';
import TreatmentPage from './pages/TreatmentPage.vue';
import BruxismPage from './pages/BruxismPage.vue';
import PatientInfoPage from './pages/PatientInfoPage.vue';
import SelectPatientPage from './pages/SelectPatientPage.vue'

const app = createApp(App)
app.use(VueRouter.createRouter({
   history: VueRouter.createWebHistory(process.env.BASE_URL),
    routes:[{
        path: '/',
        component: HomePage,
    }, {
        path: '/sleep',
        component: SleepPage,
        name: 'SleepPage',
        props: true
    }, {
        path: '/treatment',
        component: TreatmentPage,
    },{
        path: '/bruxism',
        component: BruxismPage,
    },{
        path: '/patient',
        component: PatientInfoPage,
    },{
        path: '/select-patient',
        component: SelectPatientPage,
        props: true
    }] 
}))
app.use(ElementPlus, {
    locale: en,
})
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.mount('#app')
