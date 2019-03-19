import Configs from './components/Configs.vue'
import Settings from './components/Settings.vue'
import Cohort from './components/Cohort.vue'
import Sumos from './components/Sumos.vue'
import Sumo from './components/Sumo.vue'


export const routes = [	
	{ name: 'cohort', path: '/cohorts/:id', component: Cohort, props: true },
	{ name: 'rondo', path: '/rondo', component: Configs},
	{ name: 'sumos', path: '/sumos', component: Sumos},
	{ name: 'sumo', path: '/sumo/:id', component: Sumo, props: true},
	{ path: '/matched', component: Settings },

]