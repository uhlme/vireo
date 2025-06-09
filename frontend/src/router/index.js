// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import CreatePlanView from '../views/CreatePlanView.vue'
import FarmerListView from '../views/FarmerListView.vue'
import CreateFarmerView from '../views/CreateFarmerView.vue'
// NEU: Die Detail-View importieren
import PlanDetailView from '../views/PlanDetailView.vue'
import EditPlanView from '../views/EditPlanView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/plan/erstellen', name: 'create-plan', component: CreatePlanView },
  { path: '/landwirte', name: 'farmer-list', component: FarmerListView },
  { path: '/landwirte/neu', name: 'create-farmer', component: CreateFarmerView },
  // NEU: Route für die Plan-Detailseite
  {
    path: '/plan/detail/:id',
    name: 'plan-detail',
    component: PlanDetailView
  },
  // NEU:
  {
    path: '/plan/bearbeiten/:id',
    name: 'edit-plan',
    component: EditPlanView
  },
  { path: '/about', name: 'about', component: () => import('../views/AboutView.vue') }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router