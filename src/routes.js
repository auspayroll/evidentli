import Configs from './components/Configs.vue'
import Settings from './components/Settings.vue'
import Cohort from './components/Cohort.vue'


export const routes = [	
	{ name: 'cohort', path: '/cohorts/:id', component: Cohort, props: true },
	{ name: 'configs', path: '/configs', component: Configs},
	{ path: '/matched', component: Settings },

]