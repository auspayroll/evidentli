import Vue from 'vue'
import App from './App'
//import router from './router'
import VueRouter from 'vue-router'
import { routes } from './routes'
import VueFlashMessage from 'vue-flash-message';
import numeral from 'numeral'

Vue.use(VueFlashMessage);
Vue.use(VueRouter);
Vue.filter('capitalize', function (value) {
  if (!value) return ''
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
})

Vue.filter("numeric", function (value, precision) {

	if(precision == null){
		precision = 4
	} else if(precision < 0){
		precision = 0
	} else if(precision > 14){
		precision = 14
	}

	var zeros = '[.]' + '0'.repeat(precision)
	if(zeros == '[.]'){
		zeros = ''
	}
    return numeral(value).format("0,0" + zeros); // displaying other groupings/separators is possible, look at the docs
 });


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

