'use client';

import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { VisualizationProps } from '@/types';

export default function Visualization({ config, data = [] }: VisualizationProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    // Configure chart based on type
    const option = generateChartOption(config, data);
    chartInstance.current.setOption(option);

    // Handle resize
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, [config, data]);

  if (!config) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center text-gray-500">
        <p>暂无可视化配置</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
          </svg>
          数据可视化
        </h3>
      </div>
      <div className="p-4">
        {config.chart_type === 'table' ? (
          renderTable(data, config)
        ) : (
          <div ref={chartRef} style={{ width: '100%', height: '400px' }} />
        )}
      </div>
    </div>
  );
}

function generateChartOption(config: any, data: any[]) {
  const baseOption = {
    title: {
      text: config.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
      },
    },
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
  };

  switch (config.chart_type) {
    case 'bar':
      return {
        ...baseOption,
        xAxis: {
          type: 'category' as const,
          data: config.series?.[0]?.data?.map((item: any) => item[0]) || [],
          axisLabel: {
            rotate: 45,
            interval: 0,
          },
        },
        yAxis: {
          type: 'value' as const,
          name: config.y_axis || '数值',
        },
        series: [
          {
            name: config.series?.[0]?.name || '数值',
            type: 'bar' as const,
            data: config.series?.[0]?.data?.map((item: any) => item[1]) || [],
            itemStyle: {
              color: '#4f46e5',
            },
          },
        ],
      };

    case 'line':
      return {
        ...baseOption,
        xAxis: {
          type: 'category' as const,
          data: config.series?.[0]?.data?.map((item: any) => item[0]) || [],
        },
        yAxis: {
          type: 'value' as const,
          name: config.y_axis || '数值',
        },
        series: [
          {
            name: config.series?.[0]?.name || '数值',
            type: 'line' as const,
            data: config.series?.[0]?.data?.map((item: any) => item[1]) || [],
            smooth: true,
            areaStyle: {
              opacity: 0.3,
            },
            itemStyle: {
              color: '#4f46e5',
            },
          },
        ],
      };

    case 'pie':
      return {
        ...baseOption,
        tooltip: {
          trigger: 'item' as const,
          formatter: '{a} <br/>{b}: {c} ({d}%)',
        },
        series: [
          {
            name: config.series?.[0]?.name || '占比',
            type: 'pie' as const,
            radius: ['40%', '70%'],
            data: config.series?.[0]?.data || [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
          },
        ],
      };

    case 'scatter':
      return {
        ...baseOption,
        xAxis: {
          name: config.x_axis || 'X轴',
          type: 'value' as const,
          scale: true,
        },
        yAxis: {
          name: config.y_axis || 'Y轴',
          type: 'value' as const,
          scale: true,
        },
        series: [
          {
            type: 'scatter' as const,
            data: config.series?.[0]?.data || [],
            symbolSize: 10,
            itemStyle: {
              color: '#4f46e5',
            },
          },
        ],
      };

    default:
      return baseOption;
  }
}

function renderTable(data: any[], config: any) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <p>暂无数据</p>
      </div>
    );
  }

  const headers = Object.keys(data[0]);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((header, idx) => (
              <th
                key={idx}
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIdx) => (
            <tr key={rowIdx} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {headers.map((header, colIdx) => (
                <td
                  key={colIdx}
                  className="px-4 py-3 whitespace-nowrap text-sm text-gray-900"
                >
                  {String(row[header] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
