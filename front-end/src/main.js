import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import en from 'element-plus/dist/locale/en.mjs'
import App from './App.vue'
import './main.css';
import * as VueRouter from 'vue-router'
import HomePage from './pages/HomePage.vue';
import EcgPage from './pages/EcgPage.vue';
import EegMegPage from './pages/EegMegPage.vue';
import BruxismPage from './pages/BruxismPage.vue';

const app = createApp(App)
app.use(VueRouter.createRouter({
   history: VueRouter.createWebHistory(process.env.BASE_URL),
    routes:[{
        path: '/',
        component: HomePage,
    }, {
        path: '/sleep',
        component: EcgPage,
    }, {
        path: '/treatment',
        component: EegMegPage,
    },{
        path: '/bruxism',
        component: BruxismPage,
    },] 
}))
app.use(ElementPlus, {
    locale: en,
})
app.mount('#app')
