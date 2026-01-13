import React, { useState } from 'react';
import { Button, Card, Empty, message } from 'antd';
import { Upload, Search } from 'lucide-react';
import { ApiTree } from '../components/api-repository/ApiTree';
import { ApiList } from '../components/api-repository/ApiList';
import { ApiDetail } from '../components/api-repository/ApiDetail';
import { ImportApiModal } from '../components/api-repository/ImportApiModal';
import { MOCK_API_DATA } from '../components/api-repository/data';
import type { ApiTag, ApiEndpoint } from '../components/api-repository/types';
import type { RcFile } from 'antd/es/upload';
import type { DataNode } from 'antd/es/tree';

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
    console.log('Importing:', values);
    setIsImportModalOpen(false);
    message.success('API Definition imported successfully (Mock)');
  };

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col p-6 gap-6">
      {/* Top Action Bar */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">API 仓库</h1>
          <p className="text-slate-400">管理和探索您的服务 API 定义</p>
        </div>
        <Button 
          type="primary" 
          icon={<Upload size={16} />} 
          onClick={() => setIsImportModalOpen(true)}
          className="bg-indigo-600 hover:bg-indigo-500 border-none h-10 px-6"
        >
          导入 OpenAPI/Swagger
        </Button>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Left Tree */}
        <Card 
          className="w-80 flex flex-col border-slate-700/50 bg-slate-800/50 backdrop-blur-sm"
          styles={{ body: { padding: '12px', flex: 1, overflowY: 'auto' } }}
        >
          <div className="mb-4 px-2">
             <div className="relative">
                <Search className="absolute left-3 top-2.5 text-slate-500" size={14} />
                <input 
                  type="text" 
                  placeholder="Search services..." 
                  className="w-full bg-slate-900/50 border border-slate-700 rounded-md py-2 pl-9 pr-3 text-sm text-slate-300 focus:outline-none focus:border-indigo-500 transition-colors"
                />
             </div>
          </div>
          <ApiTree data={MOCK_API_DATA} onSelect={handleTreeSelect} />
        </Card>

        {/* Right Content */}
        <div className="flex-1 overflow-y-auto min-w-0">
          {selectedEndpoint ? (
            <ApiDetail endpoint={selectedEndpoint} />
          ) : selectedTag ? (
            <ApiList endpoints={selectedTag.endpoints} />
          ) : (
            <div className="h-full flex items-center justify-center bg-slate-800/30 border border-slate-700/30 rounded-lg">
              <Empty description={<span className="text-slate-400">Select a tag or endpoint to view details</span>} />
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
