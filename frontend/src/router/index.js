import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SessionView from '../views/SessionView.vue'
import SummaryView from '../views/SummaryView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/session/:id',
      name: 'session',
      component: SessionView,
    },
    {
      path: '/session/:id/summary',
      name: 'summary',
      component: SummaryView,
    },
  ],
})

export default router
