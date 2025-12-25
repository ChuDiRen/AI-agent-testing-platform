import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { useI18n } from "@/hooks/useI18n";

// 智能体元数据类型
export interface AgentMetadata {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  tags: string[];
  version?: string;
  is_streaming?: boolean;
}

// 预定义的智能体列表 (与后端 agents_config.py 保持同步)
export const AGENTS_LIST: AgentMetadata[] = [
  // Text-to-SQL 系列
  {
    id: "text2sql_agent",
    name: "Text2SQL 智能体",
    description: "自然语言转SQL查询，支持多轮对话、Schema分析、SQL生成与执行",
    icon: "🗄️",
    category: "数据分析",
    tags: ["SQL", "数据库", "自然语言"],
  },
  {
    id: "text2sql_stream",
    name: "Text2SQL (流式)",
    description: "自然语言转SQL查询，支持流式输出",
    icon: "🗄️",
    category: "数据分析",
    tags: ["SQL", "流式"],
    is_streaming: true,
  },
  // Text-to-TestCase 系列
  {
    id: "text2testcase_agent",
    name: "测试用例生成",
    description: "根据需求自动生成测试用例，支持需求分析、测试点设计、用例编写",
    icon: "🧪",
    category: "测试工具",
    tags: ["测试用例", "自动化"],
  },
  {
    id: "text2testcase_stream",
    name: "测试用例生成 (流式)",
    description: "测试用例生成，支持流式输出",
    icon: "🧪",
    category: "测试工具",
    tags: ["测试用例", "流式"],
    is_streaming: true,
  },
  // SQL Agent 系列
  {
    id: "sql_agent",
    name: "SQL Agent (基础)",
    description: "基础SQL查询智能体",
    icon: "📊",
    category: "数据分析",
    tags: ["SQL", "基础"],
  },
  {
    id: "sql_agent_hitl",
    name: "SQL Agent (人机协作)",
    description: "支持人工介入的SQL智能体",
    icon: "🤝",
    category: "数据分析",
    tags: ["SQL", "HITL"],
  },
  {
    id: "sql_agent_graph",
    name: "SQL Agent (图模式)",
    description: "基于图工作流的SQL智能体",
    icon: "🔀",
    category: "数据分析",
    tags: ["SQL", "图工作流"],
  },
  {
    id: "api_agent",
    name: "API 测试智能体",
    description: "自动化API测试智能体",
    icon: "🔌",
    category: "测试工具",
    tags: ["API", "接口测试"],
  },
];

// 分类列表
const CATEGORIES = ["全部", "数据分析", "测试工具"];

interface AgentSelectorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  currentAgentId: string;
  onSelect: (agentId: string) => void;
}

export function AgentSelector({
  open,
  onOpenChange,
  currentAgentId,
  onSelect,
}: AgentSelectorProps) {
  const { t } = useI18n();
  const [selectedCategory, setSelectedCategory] = useState("全部");
  const [searchTerm, setSearchTerm] = useState("");

  // 过滤智能体
  const filteredAgents = AGENTS_LIST.filter((agent) => {
    const matchCategory =
      selectedCategory === "全部" || agent.category === selectedCategory;
    const matchSearch =
      searchTerm === "" ||
      agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.tags.some((tag) =>
        tag.toLowerCase().includes(searchTerm.toLowerCase())
      );
    return matchCategory && matchSearch;
  });

  // 按分类分组
  const groupedAgents = filteredAgents.reduce((acc, agent) => {
    if (!acc[agent.category]) {
      acc[agent.category] = [];
    }
    acc[agent.category].push(agent);
    return acc;
  }, {} as Record<string, AgentMetadata[]>);

  const handleSelect = (agentId: string) => {
    onSelect(agentId);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span className="text-xl">🤖</span>
            选择智能体
          </DialogTitle>
        </DialogHeader>

        {/* 搜索和分类过滤 */}
        <div className="flex flex-col gap-3 py-2">
          {/* 搜索框 */}
          <input
            type="text"
            placeholder="搜索智能体..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          />

          {/* 分类标签 */}
          <div className="flex gap-2 flex-wrap">
            {CATEGORIES.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category)}
                className="text-xs"
              >
                {category}
              </Button>
            ))}
          </div>
        </div>

        {/* 智能体列表 */}
        <div className="flex-1 overflow-y-auto pr-2 -mr-2">
          {Object.entries(groupedAgents).map(([category, agents]) => (
            <div key={category} className="mb-4">
              <h3 className="text-sm font-medium text-muted-foreground mb-2 sticky top-0 bg-background py-1">
                {category}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {agents.map((agent) => (
                  <AgentCard
                    key={agent.id}
                    agent={agent}
                    isSelected={agent.id === currentAgentId}
                    onSelect={() => handleSelect(agent.id)}
                  />
                ))}
              </div>
            </div>
          ))}

          {filteredAgents.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              没有找到匹配的智能体
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// 智能体卡片组件
interface AgentCardProps {
  agent: AgentMetadata;
  isSelected: boolean;
  onSelect: () => void;
}

function AgentCard({ agent, isSelected, onSelect }: AgentCardProps) {
  return (
    <div
      onClick={onSelect}
      className={cn(
        "p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md",
        isSelected
          ? "border-primary bg-primary/5 ring-1 ring-primary"
          : "border-border hover:border-primary/50"
      )}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{agent.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-sm truncate">{agent.name}</h4>
            {agent.is_streaming && (
              <span className="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">
                流式
              </span>
            )}
            {isSelected && (
              <span className="text-xs px-1.5 py-0.5 bg-green-100 text-green-700 rounded">
                当前
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
            {agent.description}
          </p>
          <div className="flex gap-1 mt-2 flex-wrap">
            {agent.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-xs px-1.5 py-0.5 bg-muted rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// 智能体快速切换按钮 (用于顶部导航)
interface AgentSwitchButtonProps {
  currentAgentId: string;
  onClick: () => void;
}

export function AgentSwitchButton({
  currentAgentId,
  onClick,
}: AgentSwitchButtonProps) {
  const currentAgent = AGENTS_LIST.find((a) => a.id === currentAgentId);

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={onClick}
      className="gap-2 max-w-[200px]"
    >
      <span>{currentAgent?.icon || "🤖"}</span>
      <span className="truncate">{currentAgent?.name || currentAgentId}</span>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </Button>
  );
}

export default AgentSelector;
