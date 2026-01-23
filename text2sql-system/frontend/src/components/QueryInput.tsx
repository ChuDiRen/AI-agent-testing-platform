'use client';

import React, { useState } from 'react';
import { QueryInputProps } from '@/types';

export default function QueryInput({ onQuery, isProcessing, disabled = false }: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [examples] = useState([
    '查找购买金额最高的前10个客户',
    '统计每个国家的客户数量',
    '显示所有艺术家及其专辑数量',
    '查找最畅销的5首歌曲',
    '分析每月的销售趋势',
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isProcessing) {
      onQuery(query.trim());
    }
  };

  const handleExampleClick = (example: string) => {
    if (!isProcessing) {
      setQuery(example);
      onQuery(example);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Query Input Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="请输入您的查询，例如：查找购买金额最高的前10个客户"
            disabled={disabled || isProcessing}
            rows={4}
            className="w-full px-4 py-3 pr-32 text-lg border-2 border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={disabled || isProcessing || !query.trim()}
            className="absolute bottom-3 right-3 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {isProcessing ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
            ) : (
              '提交查询'
            )}
          </button>
        </div>
      </form>

      {/* Example Queries */}
      <div className="mt-6">
        <p className="text-sm text-gray-600 mb-3 font-medium">示例查询：</p>
        <div className="flex flex-wrap gap-2">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example)}
              disabled={disabled || isProcessing}
              className="px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 hover:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
