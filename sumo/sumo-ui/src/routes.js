import Sumo from './components/Sumo.vue'
import Sumos from './components/Sumos.vue'
import Project from './Project.vue'
import App from './App.vue'
import CreateSumo from './components/CreateSumo.vue'


export const routes = [	
	{ name: 'sumo', path: '/projects/:projectId/sumos/:id', component: Sumo, props: true },
	{ name: 'createSumo', path: '/projects/:projectId/sumo/create', component: CreateSumo, props: true },
	{ name: 'sumos', path: '/projects/:projectId/sumos', component: Sumos, props: true },
	{ name: 'project', path: '/projects/:projectId', component: Project, props: true }

]