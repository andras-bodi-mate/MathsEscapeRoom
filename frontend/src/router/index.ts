import { createRouter, createWebHistory } from 'vue-router';
import type { RouteLocationNormalized } from 'vue-router';
import ExerciseView from '@/views/ExerciseView.vue';
import RegistrationView from '@/components/Registration.vue';
import ResultsView from '@/views/ResultsView.vue';
import AdminPanelView from '@/views/AdminPanelView.vue';

const routes = [
  {
    path: "/",
    redirect: "/regisztracio"
  },
  {
    path: "/regisztracio",
    component: RegistrationView
  },
  {
    path: "/eredmenyek",
    component: ResultsView
  },
  {
    path: "/kezelofelulet",
    component: AdminPanelView
  },
  {
    path: "/feladat/:level(\\d+)",
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