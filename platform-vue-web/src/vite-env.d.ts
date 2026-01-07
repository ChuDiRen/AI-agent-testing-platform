/// <reference types="vite/client" />

// 为 ~ 别名创建模块声明,解决 Vetur/TypeScript 路径解析问题
declare module '~/*' {
  const value: any;
  export default value;
}

// 声明组件模块类型
declare module '~/components/BaseSearch/index.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent;
  export default component;
}

declare module '~/components/BaseTable/index.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent;
  export default component;
}

declare module '~/components/CodeEditor.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent;
  export default component;
}

declare module '~/components/JsonViewer.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent;
  export default component;
}

declare module '~/components/YamlViewer.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent;
  export default component;
}

// 声明工具函数模块类型
declare module '~/utils/timeFormatter' {
  export function formatDateTime(timestamp: string | number | Date): string;
}

// 声明 API 模块类型
declare module '~/views/login/login' {
  export function getUserInfo(): Promise<any>;
}

declare module '~/views/login/login.js' {
  export function getUserInfo(): Promise<any>;
}

declare module '~/views/system/menu/menu' {
  export function getUserMenus(uid: number): Promise<any>;
  export function getMenuTree(): Promise<any>;
}

declare module '~/views/system/dept/dept' {
  export function getDeptTree(): Promise<any>;
}

declare module '~/views/apitest/project/apiProject' {
  export function queryAllProject(): Promise<any>;
}

declare module '~/views/apitest/project/apiProject.js' {
  export function queryAllProject(): Promise<any>;
}
