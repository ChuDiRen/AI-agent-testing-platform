import { type ThemeConfig, theme } from 'antd';

export const cyberpunkTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#6366f1', // Indigo-500
    colorInfo: '#6366f1',
    colorSuccess: '#22c55e',
    colorWarning: '#eab308',
    colorError: '#ef4444',
    colorBgBase: '#0f172a', // Slate-900
    fontFamily: 'Inter, sans-serif',
    borderRadius: 6,
    wireframe: false,
  },
  components: {
    Input: {
      colorBgContainer: 'rgba(30, 41, 59, 0.5)', // bg-slate-800/50
      colorBorder: 'rgba(51, 65, 85, 0.5)', // border-slate-700/50
      activeBorderColor: '#6366f1',
      hoverBorderColor: '#818cf8',
      colorTextPlaceholder: '#94a3b8', // Slate-400
    },
    Button: {
      colorPrimary: '#6366f1',
      algorithm: true, // Enable algorithm for button states
    },
    Form: {
      labelColor: '#cbd5e1', // Slate-300
    },
    Typography: {
      colorTextHeading: '#f8fafc', // Slate-50
      colorText: '#e2e8f0', // Slate-200
    }
  }
};
