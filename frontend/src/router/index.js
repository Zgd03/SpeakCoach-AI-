import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/HomeView.vue"),
  },
  {
    path: "/chat/:sessionId",
    name: "Chat",
    component: () => import("../views/ChatView.vue"),
    props: true,
  },
  {
    path: "/summary/:sessionId",
    name: "Summary",
    component: () => import("../views/SummaryView.vue"),
    props: true,
  },
  {
    path: "/history",
    name: "History",
    component: () => import("../views/HistoryView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
