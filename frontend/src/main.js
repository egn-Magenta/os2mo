// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from 'vue'
import Router from 'vue-router'
import App from './App'
import router from './router'
import i18n from './i18n.js'
import VueShortKey from 'vue-shortkey'
import store from './store'
import { sync } from 'vuex-router-sync'
import VueSplit from 'vue-split-panel'
import FlagIcon from 'vue-flag-icon'
import './vee.js'
import '@babel/polyfill'
import './icons.js'
import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/global.css'
import 'moment/locale/da'  // TODO: do we need to load other locales?

import '@/views/employee/install'
import '@/views/organisation/install'
import '@/modules/install'
import Keycloak from 'keycloak-js'

sync(store, router)

Vue.config.productionTip = false

let keycloak = Keycloak(window.location.origin + '/service/keycloak.json')

keycloak.init({ onLoad: 'login-required' }).then((auth) => {
  if (!auth) {
    window.location.reload();
  } else {
    console.log("Authenticated")

    Vue.use(VueShortKey, { prevent: ['input', 'textarea'] })
    Vue.use(VueSplit)
    Vue.use(FlagIcon)
    Vue.use(Router)

    new Vue({
      router,
      store,
      i18n,
      render: h => h(App)
    }).$mount('#app')

  }

  // Token refresh
  setInterval(() => {
    keycloak.updateToken(15).then((refreshed) => {
      if (refreshed) {
        console.debug('Token refreshed')
        console.debug(keycloak.tokenParsed)
      } else {
        console.debug('Token not refreshed, valid for '
          + Math.round(keycloak.tokenParsed.exp + keycloak.timeSkew - new Date().getTime() / 1000) + ' seconds')
      }
    }).catch(() => {
      console.error('Failed to refresh token')
    });
  }, 5000)

}).catch(() => {
  console.error("Authenticated Failed")
});

export default keycloak
