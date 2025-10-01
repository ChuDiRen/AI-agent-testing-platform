import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetTypography,
  presetUno,
  presetWebFonts,
  transformerAttributifyJsx,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

export default defineConfig({
  shortcuts: [
    // 布局相关
    ['wh-full', 'w-full h-full'],
    ['f-c-c', 'flex justify-center items-center'],
    ['flex-col', 'flex flex-col'],
    ['flex-center', 'flex justify-center items-center'],
    ['flex-between', 'flex justify-between items-center'],
    ['flex-around', 'flex justify-around items-center'],
    ['flex-evenly', 'flex justify-evenly items-center'],
    ['flex-col-center', 'flex flex-col justify-center items-center'],
    ['flex-col-between', 'flex flex-col justify-between items-center'],
    ['absolute-lt', 'absolute left-0 top-0'],
    ['absolute-lb', 'absolute left-0 bottom-0'],
    ['absolute-rt', 'absolute right-0 top-0'],
    ['absolute-rb', 'absolute right-0 bottom-0'],
    ['absolute-center', 'absolute-lt f-c-c wh-full'],

    // 文本相关
    ['text-ellipsis', 'truncate'],
    ['text-break', 'break-all'],

    // 边框相关
    ['border-base', 'border border-gray-200 dark:border-gray-700'],
    ['border-hover', 'border-gray-300 dark:border-gray-600'],

    // 阴影相关
    ['shadow-base', 'shadow-sm'],
    ['shadow-hover', 'shadow-md'],
    ['card-shadow', 'shadow-[0_1px_2px_-2px_#00000029,0_3px_6px_#0000001f,0_5px_12px_4px_#00000017]'],
    
    // 过渡动画
    ['transition-base', 'transition-all duration-300 ease-in-out'],
    ['transition-fast', 'transition-all duration-150 ease-in-out'],
    ['transition-slow', 'transition-all duration-500 ease-in-out'],
    
    // 按钮样式
    ['btn-base', 'px-4 py-2 rounded-md transition-base'],
    ['btn-primary', 'btn-base bg-blue-500 text-white hover:bg-blue-600'],
    ['btn-secondary', 'btn-base bg-gray-500 text-white hover:bg-gray-600'],
    
    // 输入框样式
    ['input-base', 'px-3 py-2 border-base rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'],
    
    // 卡片样式
    ['card-base', 'bg-white dark:bg-gray-800 border-base rounded-lg p-4'],
    ['card-hover', 'card-base hover:shadow-hover transition-base cursor-pointer'],
  ],
  
  theme: {
    colors: {
      primary: {
        50: '#eff6ff',
        100: '#dbeafe',
        200: '#bfdbfe',
        300: '#93c5fd',
        400: '#60a5fa',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
        800: '#1e40af',
        900: '#1e3a8a',
      },
      gray: {
        50: '#f9fafb',
        100: '#f3f4f6',
        200: '#e5e7eb',
        300: '#d1d5db',
        400: '#9ca3af',
        500: '#6b7280',
        600: '#4b5563',
        700: '#374151',
        800: '#1f2937',
        900: '#111827',
      },
    },
    breakpoints: {
      xs: '480px',
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    },
  },
  
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
    presetTypography(),
    presetWebFonts({
      fonts: {
        sans: 'Inter:400,500,600,700',
        mono: 'Fira Code:400,500,600',
      },
    }),
  ],
  
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
    transformerAttributifyJsx(),
  ],
  
  safelist: [
    'prose',
    'prose-sm',
    'prose-lg',
    'prose-xl',
    'prose-2xl',
  ],
})
