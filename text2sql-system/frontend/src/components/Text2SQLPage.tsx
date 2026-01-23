'use client';

import React, { useState, useCallback, useRef } from 'react';
import QueryInput from './QueryInput';
import OutputRegion from './OutputRegion';
import Visualization from './Visualization';
import { useWebSocket } from './WebSocketClient';
import { WebSocketResponse, QueryState } from '@/types';

export default function Text2SQLPage() {
  const [queryState, setQueryState] = useState<QueryState | null>(null);
  const [agentOutputs, setAgentOutputs] = useState<Record<string, string>>({});
  const wsRef = useRef<any>(null);

  // WebSocket connection
  const { status, sendMessage, connect } = useWebSocket('ws://localhost:8000/api/text2sql/websocket');

  // Initialize WebSocket connection on mount
  React.useEffect(() => {
    connect(
      // onMessage
      (message: WebSocketResponse) => {
        handleWebSocketMessage(message);
      },
      // onError
      (error) => {
        console.error('WebSocket error:', error);
        setQueryState((prev) => prev ? { ...prev, status: 'error', error: '连接错误' } : null);
      },
      // onOpen
      () => {
        console.log('WebSocket connected');
      },
      // onClose
      () => {
        console.log('WebSocket disconnected');
      }
    );
  }, [connect]);

  const handleWebSocketMessage = (message: WebSocketResponse) => {
    console.log('Received message:', message);

    // Update agent outputs
    setAgentOutputs((prev) => ({
      ...prev,
      [message.source]: message.content,
    }));

    // Handle final result
    if (message.is_final && message.result) {
      setQueryState({
        id: Date.now().toString(),
        query: queryState?.query || '',
        status: 'completed',
        results: {
          analysis: agentOutputs['query_analyzer'],
          sql: message.result.sql,
          explanation: agentOutputs['sql_explainer'],
          data: message.result.data,
          statistics: message.result.statistics,
          visualization: message.result.visualization,
        },
        timestamp: Date.now(),
      });
    }
  };

  const handleQuery = useCallback((query: string) => {
    // Reset state for new query
    setQueryState({
      id: Date.now().toString(),
      query,
      status: 'processing',
      results: {},
      timestamp: Date.now(),
    });
    setAgentOutputs({});

    // Send query via WebSocket
    sendMessage(query);
  }, [sendMessage]);

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'bg-green-100 text-green-800';
      case 'connecting':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return '已连接';
      case 'connecting':
        return '连接中...';
      case 'error':
        return '连接错误';
      default:
        return '未连接';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Text2SQL 智能查询系统</h1>
              <p className="mt-1 text-sm text-gray-600">
                基于AutoGen多智能体协作的自然语言到SQL转换平台
              </p>
            </div>
            <div className="flex items-center gap-4">
              {/* Connection Status */}
              <div className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor()}`}>
                {getStatusText()}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Query Input Section */}
        <section className="mb-8">
          <QueryInput
            onQuery={handleQuery}
            isProcessing={queryState?.status === 'processing'}
            disabled={status !== 'connected'}
          />
        </section>

        {/* Processing Indicator */}
        {queryState?.status === 'processing' && (
          <section className="mb-8">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <div>
                  <h3 className="text-lg font-semibold text-blue-900">正在处理查询...</h3>
                  <p className="text-sm text-blue-700 mt-1">
                    请稍候，多智能体正在分析您的查询
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Results Section */}
        {queryState?.status === 'completed' && (
          <section className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">查询结果</h2>

            {/* Grid Layout for Agent Outputs */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Query Analysis */}
              <OutputRegion
                title="查询分析"
                content={queryState.results.analysis || ''}
                type="markdown"
                loading={false}
              />

              {/* Generated SQL */}
              <OutputRegion
                title="生成的SQL"
                content={queryState.results.sql || ''}
                type="code"
                loading={false}
              />

              {/* SQL Explanation */}
              <OutputRegion
                title="SQL解释"
                content={queryState.results.explanation || ''}
                type="markdown"
                loading={false}
              />

              {/* Query Data */}
              <OutputRegion
                title="查询数据"
                content={queryState.results.data ? JSON.stringify(queryState.results.data) : ''}
                type="table"
                loading={false}
              />
            </div>

            {/* Visualization */}
            {queryState.results.visualization && (
              <Visualization
                config={queryState.results.visualization}
                data={queryState.results.data}
              />
            )}

            {/* Statistics */}
            {queryState.results.statistics && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">查询统计</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600">执行时间</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                      {queryState.results.statistics.execution_time.toFixed(2)}s
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600">返回行数</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                      {queryState.results.statistics.row_count}
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600">列数</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1">
                      {queryState.results.statistics.column_count}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Error State */}
        {queryState?.status === 'error' && (
          <section className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-red-900 mb-2">查询处理失败</h3>
            <p className="text-red-700">{queryState.error}</p>
          </section>
        )}

        {/* Empty State */}
        {!queryState && (
          <section className="text-center py-16">
            <div className="inline-block p-6 rounded-full bg-indigo-100 mb-4">
              <svg
                className="w-12 h-12 text-indigo-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">开始您的查询</h3>
            <p className="text-gray-600 max-w-md mx-auto">
              在上方输入您的自然语言查询，系统将自动分析并生成相应的SQL语句
            </p>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Text2SQL 智能查询系统 - 基于 AutoGen 多智能体协作框架
          </p>
        </div>
      </footer>
    </div>
  );
}
