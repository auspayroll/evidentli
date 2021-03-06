import Rondos from './components/Rondos.vue'
import Settings from './components/Settings.vue'
import Rondo from './components/Rondo.vue'
import Sumos from './components/Sumos.vue'
import Sumo from './components/Sumo.vue'
import Project from './Project.vue'


export const routes = [	
	{ name: 'rondo', path: '/projects/:projectId/rondos/:id', component: Rondo, props: true },
	{ name: 'createRondo', path: '/projects/:projectId/rondos/new', component: Rondo, props: true },
	{ name: 'rondos', path: '/projects/:projectId/rondos', component: Rondos, props: true },
	{ name: 'project', path: '/projects/:projectId', component: Project, props: true }
	//{ name: 'sumos', path: '/sumos', component: Sumos},
	//{ name: 'sumo', path: '/sumo/:id', component: Sumo, props: true},
	//{ path: '/matched', component: Settings },

]