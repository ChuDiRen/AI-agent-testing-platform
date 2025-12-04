import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Rules from '../views/Rules.vue';
import Agents from '../views/Agents.vue';
import Knowledge from '../views/Knowledge.vue';
import Plugins from '../views/Plugins.vue';
import MCP from '../views/MCP.vue';
import Prompt from '../views/Prompt.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/index.html', redirect: '/' }, // Handle legacy link
  { path: '/rules', name: 'Rules', component: Rules },
  { path: '/rules.html', redirect: '/rules' },
  { path: '/agents', name: 'Agents', component: Agents },
  { path: '/agents.html', redirect: '/agents' },
  { path: '/knowledge', name: 'Knowledge', component: Knowledge },
  { path: '/knowledge.html', redirect: '/knowledge' },
  { path: '/plugins', name: 'Plugins', component: Plugins },
  { path: '/plugins.html', redirect: '/plugins' },
  { path: '/mcp', name: 'MCP', component: MCP },
  { path: '/mcp.html', redirect: '/mcp' },
  { path: '/prompt', name: 'Prompt', component: Prompt },
  { path: '/prompt.html', redirect: '/prompt' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
