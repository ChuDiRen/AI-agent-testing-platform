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
        <span className="flex items-center gap-2 text-slate-700 font-medium">
          <Box size={14} className="text-blue-600" />
          {service.name}
        </span>
      ),
      key: service.id,
      children: service.versions.map((version) => ({
        title: (
          <span className="flex items-center gap-2 text-slate-600">
            <GitBranch size={14} className="text-purple-600" />
            {version.version}
          </span>
        ),
        key: version.id,
        children: version.tags.map((tag) => ({
          title: (
            <span className="flex items-center gap-2 text-slate-500">
              <Tag size={14} className="text-slate-400" />
              {tag.name}
            </span>
          ),
          key: tag.id,
          data: tag, // Store the tag data for retrieval
          children: tag.endpoints.map((ep) => ({
            title: (
              <span className="flex items-center gap-2 text-slate-500 text-xs font-mono">
                <FileCode size={12} />
                <span className={`uppercase font-semibold ${ep.method === 'GET' ? 'text-blue-600' :
                    ep.method === 'POST' ? 'text-green-600' :
                      ep.method === 'DELETE' ? 'text-red-600' :
                        'text-orange-600'
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
        switcherIcon={<ChevronDown size={14} className="text-slate-400" />}
        onSelect={onSelect}
        treeData={treeData as DataNode[]}
        className="bg-transparent text-slate-700"
        blockNode
      />
    </div>
  );
};
