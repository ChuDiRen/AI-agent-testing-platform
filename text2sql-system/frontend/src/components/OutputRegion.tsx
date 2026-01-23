'use client';

import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { OutputRegionProps } from '@/types';
import ReactMarkdown from 'react-markdown';

export default function OutputRegion({ title, content, type, loading = false, error }: OutputRegionProps) {
  const renderContent = () => {
    if (error) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center gap-2 text-red-600 font-medium">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            错误
          </div>
          <p className="mt-2 text-red-700 text-sm">{error}</p>
        </div>
      );
    }

    if (loading) {
      return (
        <div className="p-8 text-center text-gray-500">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
          <p>加载中...</p>
        </div>
      );
    }

    if (!content) {
      return (
        <div className="p-8 text-center text-gray-400">
          <p>暂无内容</p>
        </div>
      );
    }

    switch (type) {
      case 'markdown':
        return (
          <div className="prose prose-sm max-w-none prose-slate">
            <ReactMarkdown
              components={{
                code: ({ className, children, ...props }: any) => {
                  const match = /language-(\w+)/.exec(className || '');
                  return match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className="bg-gray-100 px-1 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        );

      case 'code':
        return (
          <div className="rounded-md overflow-hidden">
            <SyntaxHighlighter
              style={vscDarkPlus}
              language="sql"
              showLineNumbers={true}
              wrapLines={true}
              customStyle={{ margin: 0 }}
            >
              {content}
            </SyntaxHighlighter>
          </div>
        );

      case 'json':
        try {
          const parsed = JSON.stringify(JSON.parse(content), null, 2);
          return (
            <div className="rounded-md overflow-auto max-h-96">
              <SyntaxHighlighter
                style={vscDarkPlus}
                language="json"
                showLineNumbers={true}
                customStyle={{ margin: 0 }}
              >
                {parsed}
              </SyntaxHighlighter>
            </div>
          );
        } catch {
          return <pre className="whitespace-pre-wrap text-sm">{content}</pre>;
        }

      case 'table':
        try {
          const data = JSON.parse(content);
          if (!Array.isArray(data) || data.length === 0) {
            return <div className="p-4 text-gray-500">无数据</div>;
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
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
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
                          className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
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
        } catch (e) {
          return (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-yellow-700 text-sm">无法解析表格数据</p>
              <pre className="mt-2 text-xs">{content}</pre>
            </div>
          );
        }

      default:
        return <pre className="whitespace-pre-wrap text-sm">{content}</pre>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      </div>
      <div className="p-4 max-h-96 overflow-y-auto">
        {renderContent()}
      </div>
    </div>
  );
}
