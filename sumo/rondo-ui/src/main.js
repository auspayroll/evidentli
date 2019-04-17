import Vue from 'vue'
import App from './App'
//import router from './router'
import VueRouter from 'vue-router'
import { routes } from './routes'
import VueFlashMessage from 'vue-flash-message';

Vue.use(VueFlashMessage);
Vue.use(VueRouter);
require('vue-flash-message/dist/vue-flash-message.min.css');

const router = new VueRouter({
	routes
});

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})

