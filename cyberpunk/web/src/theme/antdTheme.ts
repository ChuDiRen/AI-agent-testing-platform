import { type ThemeConfig, theme } from 'antd';

export const modernTheme: ThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#2563EB', // Blue 600
    colorInfo: '#2563EB',
    colorSuccess: '#10B981', // Emerald 500
    colorWarning: '#F59E0B', // Amber 500
    colorError: '#EF4444',   // Red 500
    colorBgBase: '#ffffff',
    colorBgContainer: '#ffffff',
    fontFamily: 'Inter, sans-serif',
    borderRadius: 8,
    wireframe: false,
    fontSize: 14,
  },
  components: {
    Layout: {
      bodyBg: '#F8FAFC', // Slate 50
      headerBg: '#ffffff',
      siderBg: '#ffffff',
    },
    Input: {
      colorBgContainer: '#ffffff',
      colorBorder: '#E2E8F0', // Slate 200
      activeBorderColor: '#2563EB',
      hoverBorderColor: '#3B82F6',
      colorTextPlaceholder: '#94A3B8', // Slate 400
      borderRadius: 6,
    },
    Button: {
      fontWeight: 500,
      borderRadius: 6,
      controlHeight: 36,
    },
    Card: {
      colorBgContainer: '#ffffff',
      colorBorderSecondary: '#E2E8F0',
      borderRadius: 12,
      boxShadowSecondary: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    },
    Table: {
      colorBgContainer: '#ffffff',
      headerBg: '#F8FAFC', // Slate 50
      rowHoverBg: '#F1F5F9', // Slate 100
      borderColor: '#E2E8F0',
    },
    Menu: {
      itemBg: '#ffffff',
      itemSelectedColor: '#2563EB',
      itemSelectedBg: '#EFF6FF', // Blue 50
      itemColor: '#64748B', // Slate 500
    },
    Typography: {
      colorTextHeading: '#0F172A', // Slate 900
      colorText: '#334155', // Slate 700
      fontFamilyCode: 'JetBrains Mono, monospace',
    }
  }
};
