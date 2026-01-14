import { type ThemeConfig, theme } from 'antd';

export const cyberpunkTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#00f3ff', // Neon Cyan
    colorInfo: '#00f3ff',
    colorSuccess: '#0aff0a', // Neon Green
    colorWarning: '#fcee0a', // Neon Yellow
    colorError: '#ff003c',   // Neon Pink/Red
    colorBgBase: '#050505',  // Deep Black
    colorBgContainer: '#121212',
    colorBgElevated: '#1a1a1a',
    fontFamily: 'Inter, sans-serif',
    borderRadius: 2, // Sharp edges for tech feel
    wireframe: false,
    fontSize: 14,
  },
  components: {
    Layout: {
      bodyBg: '#050505',
      headerBg: '#0a0a0a',
      siderBg: '#0a0a0a',
    },
    Input: {
      colorBgContainer: 'rgba(18, 18, 18, 0.8)',
      colorBorder: '#2a2a2a',
      activeBorderColor: '#00f3ff',
      hoverBorderColor: 'rgba(0, 243, 255, 0.5)',
      colorTextPlaceholder: '#555',
      borderRadius: 0, // Sharp inputs
    },
    Button: {
      colorPrimary: '#00f3ff',
      primaryColor: '#000000', // Black text on neon button
      fontWeight: 600,
      borderRadius: 0, // Sharp buttons
      defaultBorderColor: '#00f3ff',
      defaultColor: '#00f3ff',
      defaultGhostColor: '#00f3ff',
    },
    Card: {
      colorBgContainer: 'rgba(18, 18, 18, 0.6)',
      colorBorderSecondary: '#2a2a2a',
      borderRadius: 4,
      boxShadowSecondary: '0 0 10px rgba(0, 0, 0, 0.5)',
    },
    Table: {
      colorBgContainer: '#0a0a0a',
      headerBg: '#121212',
      rowHoverBg: '#1a1a1a',
      borderColor: '#2a2a2a',
    },
    Menu: {
      itemBg: '#0a0a0a',
      itemSelectedColor: '#00f3ff',
      itemSelectedBg: 'rgba(0, 243, 255, 0.1)',
    },
    Typography: {
      colorTextHeading: '#ffffff',
      colorText: '#e0e0e0',
      fontFamilyCode: 'JetBrains Mono, monospace',
    }
  }
};

