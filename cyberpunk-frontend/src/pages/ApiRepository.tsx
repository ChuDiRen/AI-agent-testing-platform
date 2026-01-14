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
import { motion } from 'framer-motion';
import { CyberCard } from '../components/CyberCard';

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
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-[calc(100vh-80px)] flex flex-col p-6 gap-6 max-w-[1600px] mx-auto w-full"
    >
      {/* Top Action Bar */}
      <div className="flex justify-between items-center">
        <motion.div 
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold font-display text-white drop-shadow-md">API 仓库</h1>
          <p className="text-slate-400 font-mono text-sm mt-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse"></span>
            管理和探索您的服务 API 定义
          </p>
        </motion.div>
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Button 
            type="primary" 
            icon={<Upload size={16} />} 
            onClick={() => setIsImportModalOpen(true)}
            className="cyber-button !h-10 px-6"
          >
            导入 OpenAPI/Swagger
          </Button>
        </motion.div>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* Left Tree */}
        <motion.div 
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="w-80 flex-shrink-0"
        >
          <CyberCard 
            className="h-full flex flex-col !p-4" 
            title="Service Explorer" 
            icon={Database}
            hoverEffect={false}
          >
            <div className="mb-4">
               <div className="relative group">
                  <Search className="absolute left-3 top-2.5 text-slate-500 group-focus-within:text-neon-cyan transition-colors" size={14} />
                  <input 
                    type="text" 
                    placeholder="Search services..." 
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-sm text-slate-300 focus:outline-none focus:border-neon-cyan/50 focus:ring-1 focus:ring-neon-cyan/50 transition-all placeholder:text-slate-600"
                  />
               </div>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar -mx-2 px-2">
              <ApiTree data={MOCK_API_DATA} onSelect={handleTreeSelect} />
            </div>
          </CyberCard>
        </motion.div>

        {/* Right Content */}
        <motion.div 
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex-1 overflow-y-auto min-w-0 rounded-xl custom-scrollbar"
        >
          {selectedEndpoint ? (
            <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/60 rounded-xl p-6 min-h-full">
              <ApiDetail endpoint={selectedEndpoint} />
            </div>
          ) : selectedTag ? (
             <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/60 rounded-xl p-6 min-h-full">
               <ApiList endpoints={selectedTag.endpoints} />
             </div>
          ) : (
            <div className="h-full flex items-center justify-center bg-slate-900/30 border border-slate-800/30 rounded-xl border-dashed">
              <Empty 
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  <div className="flex flex-col items-center gap-2">
                    <span className="text-slate-400 font-mono">Select a tag or endpoint to view details</span>
                    <span className="text-slate-600 text-xs">Waiting for input...</span>
                  </div>
                } 
              />
            </div>
          )}
        </motion.div>
      </div>

      <ImportApiModal 
        open={isImportModalOpen} 
        onCancel={() => setIsImportModalOpen(false)}
        onImport={handleImport} 
      />
    </motion.div>
  );
};

