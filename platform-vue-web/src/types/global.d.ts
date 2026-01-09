// Type declarations for Vue components and utilities
declare module '~/utils/timeFormatter' {
  export function formatDateTime(time: string | Date): string;
  export function formatDate(time: string | Date): string;
  export function getCurrentDateTime(): string;
  export function getCurrentDate(): string;
}

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
