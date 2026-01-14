import React, { useMemo } from 'react';
import { Tree } from 'antd';
import { Box, GitBranch, Tag, FileCode, ChevronDown } from 'lucide-react';
import type { DataNode } from 'antd/es/tree';
import type { ApiService } from './types';

export interface ApiTreeProps {
  data: ApiService[];
  onSelect: (selectedKeys: React.Key[], info: { node: DataNode; selected: boolean; selectedNodes: DataNode[]; nativeEvent: MouseEvent }) => void;
}

export const ApiTree: React.FC<ApiTreeProps> = ({ data, onSelect }) => {
  const treeData = useMemo(() => {
    return data.map((service) => ({
      title: (
        <span className="flex items-center gap-2 text-slate-200 font-medium">
          <Box size={14} className="text-neon-cyan" />
          {service.name}
        </span>
      ),
      key: service.id,
      children: service.versions.map((version) => ({
        title: (
          <span className="flex items-center gap-2 text-slate-300">
            <GitBranch size={14} className="text-neon-purple" />
            {version.version}
          </span>
        ),
        key: version.id,
        children: version.tags.map((tag) => ({
          title: (
            <span className="flex items-center gap-2 text-slate-400">
              <Tag size={14} className="text-slate-500" />
              {tag.name}
            </span>
          ),
          key: tag.id,
          data: tag, // Store the tag data for retrieval
          children: tag.endpoints.map((ep) => ({
            title: (
              <span className="flex items-center gap-2 text-slate-500 text-xs font-mono">
                <FileCode size={12} />
                <span className={`uppercase ${
                  ep.method === 'GET' ? 'text-blue-400' :
                  ep.method === 'POST' ? 'text-green-400' :
                  ep.method === 'DELETE' ? 'text-red-400' :
                  'text-orange-400'
                }`}>{ep.method}</span>
                {ep.path}
              </span>
            ),
            key: ep.id,
            data: ep,
            isLeaf: true,
          }))
        }))
      }))
    }));
  }, [data]);

  return (
    <div className="py-2">
      <Tree
        showLine={{ showLeafIcon: false }}
        showIcon={false}
        defaultExpandAll
        switcherIcon={<ChevronDown size={14} className="text-slate-500" />}
        onSelect={onSelect}
        treeData={treeData as DataNode[]}
        className="bg-transparent text-slate-300 api-tree"
        blockNode
      />
      <style>{`
        .api-tree .ant-tree-node-content-wrapper {
          padding: 4px 0;
          transition: all 0.2s;
        }
        .api-tree .ant-tree-node-content-wrapper:hover {
          background-color: rgba(99, 102, 241, 0.1) !important;
        }
        .api-tree .ant-tree-node-selected .ant-tree-node-content-wrapper {
          background-color: rgba(99, 102, 241, 0.2) !important;
          color: #fff !important;
        }
        .api-tree .ant-tree-switcher {
          background: transparent !important;
        }
      `}</style>
    </div>
  );
};

