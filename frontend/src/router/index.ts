import { createRouter, createWebHistory } from 'vue-router';
import type { RouteLocationNormalized } from 'vue-router'
import ExerciseView from '@/views/ExerciseView.vue';

const routes = [
  {
    path: '/feladat/:level(\\d+)',
    component: ExerciseView,
    props: (route: RouteLocationNormalized) => ({
      level: Number(route.params.level)
    })
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;