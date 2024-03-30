import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import { i18n } from './utils/i18n'

import PrimeVue from 'primevue/config'
// @ts-ignore
import Lara from './presets/Lara'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(i18n)

app.use(PrimeVue, {
  unstyled: true,
  pt: Lara
})

app.mount('#app')
