// Copyright (c) 2025 左岚. All rights reserved.
import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'

export default [
  // 基础配置
  js.configs.recommended,

  // Vue 配置 - 使用 essential 而不是 recommended
  ...vue.configs['flat/essential'],

  // TypeScript 文件配置
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module',
      },
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        navigator: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        FormData: 'readonly',
        File: 'readonly',
        Blob: 'readonly',
        Response: 'readonly',
        TextDecoder: 'readonly',
        HTMLElement: 'readonly',
      },
    },
    plugins: {
      '@typescript-eslint': typescript,
    },
    rules: {
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/ban-ts-comment": "off",
      "no-console": "off",
      "no-debugger": "warn",
      "no-var": "error",
      "prefer-const": "warn",
      "no-unused-vars": "off",
      "no-undef": "off",
      "no-empty": "off",
      "no-redeclare": "off",
    },
  },

  // Vue 文件配置
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: 2022,
        sourceType: 'module',
      },
      globals: {
        // Vue 3 Composition API
        defineProps: 'readonly',
        defineEmits: 'readonly',
        defineExpose: 'readonly',
        withDefaults: 'readonly',
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        navigator: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        FormData: 'readonly',
        File: 'readonly',
        Blob: 'readonly',
        Response: 'readonly',
        TextDecoder: 'readonly',
        HTMLElement: 'readonly',
      },
    },
    plugins: {
      vue,
      '@typescript-eslint': typescript,
    },
    rules: {
      // Vue 规则
      "vue/multi-word-component-names": "off",
      "vue/no-v-html": "off",
      "vue/no-unused-vars": "off",
      "vue/no-setup-props-destructure": "off",

      // TypeScript 规则
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/ban-ts-comment": "off",

      // 基础规则
      "no-console": "off",
      "no-debugger": "warn",
      "no-var": "error",
      "prefer-const": "warn",
      "no-unused-vars": "off",
      "no-undef": "off",
      "no-empty": "off",
      "no-redeclare": "off",
    },
  },

  // 忽略文件
  {
    ignores: ['node_modules/**', 'dist/**', '*.d.ts', 'components.d.ts', 'auto-import.d.ts'],
  },
]
