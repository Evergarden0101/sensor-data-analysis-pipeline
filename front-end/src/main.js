import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import en from 'element-plus/dist/locale/en.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import './main.css';
import * as VueRouter from 'vue-router'
import HomePage from './pages/HomePage.vue';
import FilteringPage from './pages/FilteringPage.vue';
import TreatmentPage from './pages/TreatmentPage.vue';
import EventsClassificationPage from './pages/EventsClassificationPage.vue';
import PatientDataPage from './pages/PatientDataPage.vue';
import SettingsPage from './pages/SettingsPage.vue';
import PathNotFoundPage from './pages/PathNotFoundPage.vue';
import store from './store'

const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(process.env.BASE_URL),
     routes:[{
         path: '/:pathMatch(.*)*',
         component: PathNotFoundPage
     },{
         path: '/',
         component: HomePage,
     }, {
         path: '/filtering',
         component: FilteringPage,
         name: 'FilteringPage',
         props: true
     }, {
         path: '/analysis',
         component: TreatmentPage,
     },{
         path: '/events-classification',
         component: EventsClassificationPage,
     },{
        path: '/patient-data',
        component: PatientDataPage
    }, {
        path: '/settings',
        component: SettingsPage
    }] 
 })

router.beforeEach(async (to, from, next) => {
await store.restored;
next();
});

export default router;

const app = createApp(App)
app.use(router)
app.use(ElementPlus, {
    locale: en,
})
app.use(store)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.mount('#app')

