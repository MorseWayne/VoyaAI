import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/planner',
    name: 'planner',
    component: () => import('@/views/PlannerView.vue'),
  },
  {
    path: '/plans',
    name: 'plans',
    component: () => import('@/views/PlansView.vue'),
  },
  {
    path: '/plans/create',
    name: 'create-plan',
    component: () => import('@/views/CreatePlanView.vue'),
  },
  {
    path: '/plans/:id',
    name: 'plan-detail',
    component: () => import('@/views/PlanDetailView.vue'),
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' }
  },
})

export default router
