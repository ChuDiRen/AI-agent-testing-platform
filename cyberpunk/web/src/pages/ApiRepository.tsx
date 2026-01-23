import React, { useState } from 'react';
import { Button, Empty, message } from 'antd';
import { Upload, Search, Database } from 'lucide-react';
import { ApiTree } from '../components/api-repository/ApiTree';
import { ApiList } from '../components/api-repository/ApiList';
import { ApiDetail } from '../components/api-repository/ApiDetail';
import { ImportApiModal } from '../components/api-repository/ImportApiModal';
import { MOCK_API_DATA } from '../components/api-repository/data';
import type { ApiTag, ApiEndpoint } from '../components/api-repository/types';
import type { RcFile } from 'antd/es/upload';
import type { DataNode } from 'antd/es/tree';

import { Card, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';

export interface ImportValues {
  url?: string;
  type: string;
  file?: RcFile;
}

export const ApiRepository: React.FC = () => {
  const [selectedTag, setSelectedTag] = useState<ApiTag | null>(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpoint | null>(null);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  const handleTreeSelect = (selectedKeys: React.Key[], info: { node: DataNode & { data?: ApiTag | ApiEndpoint }; selected: boolean; selectedNodes: DataNode[]; nativeEvent: MouseEvent }) => {
    if (selectedKeys.length === 0) return;

    const nodeData = info.node.data;

    if (!nodeData) {
      // Clicked on Service or Version node
      setSelectedTag(null);
      setSelectedEndpoint(null);
      return;
    }

    if ('endpoints' in nodeData) {
      // It's a Tag
      setSelectedTag(nodeData as ApiTag);
      setSelectedEndpoint(null);
    } else if ('method' in nodeData) {
      // It's an Endpoint
      setSelectedEndpoint(nodeData as ApiEndpoint);
      setSelectedTag(null);
    }
  };

  const handleImport = (values: ImportValues) => {
    console.log('正在导入:', values);
    setIsImportModalOpen(false);
    message.success('API 定义导入成功 (Mock)');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] gap-6 p-6 max-w-[1600px] mx-auto w-full">
      {/* Top Action Bar */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">API 仓库</h1>
          <p className="text-slate-500 text-sm mt-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            管理和探索您的服务 API 定义
          </p>
        </div>
        <div>
          <Button
            type="primary"
            icon={<Upload size={16} />}
            onClick={() => setIsImportModalOpen(true)}
            className="bg-primary hover:bg-blue-700 h-9"
          >
            导入 OpenAPI/Swagger
          </Button>
        </div>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Left Tree */}
        <div className="w-80 flex-shrink-0">
          <Card className="h-full flex flex-col">
            <CardContent className="p-4 flex flex-col h-full">
              <div className="flex items-center gap-2 mb-4 text-slate-900 font-semibold">
                <Database size={18} className="text-slate-400" />
                服务资源管理器
              </div>
              <div className="mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                  <Input
                    type="text"
                    placeholder="搜索服务..."
                    className="pl-9"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-y-auto -mx-2 px-2">
                <ApiTree data={MOCK_API_DATA} onSelect={handleTreeSelect} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Content */}
        <div className="flex-1 overflow-y-auto min-w-0 rounded-xl">
          {selectedEndpoint ? (
            <Card className="min-h-full">
              <CardContent className="p-6">
                <ApiDetail endpoint={selectedEndpoint} />
              </CardContent>
            </Card>
          ) : selectedTag ? (
            <Card className="min-h-full">
              <CardContent className="p-6">
                <ApiList endpoints={selectedTag.endpoints} />
              </CardContent>
            </Card>
          ) : (
            <div className="h-full flex items-center justify-center bg-slate-50 border border-slate-200 rounded-xl border-dashed">
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  <div className="flex flex-col items-center gap-2">
                    <span className="text-slate-500">选择标签或端点以查看详情</span>
                  </div>
                }
              />
            </div>
          )}
        </div>
      </div>

      <ImportApiModal
        open={isImportModalOpen}
        onCancel={() => setIsImportModalOpen(false)}
        onImport={handleImport}
      />
    </div>
  );
};
