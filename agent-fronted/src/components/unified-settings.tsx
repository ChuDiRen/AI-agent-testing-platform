import React, { useState, useMemo } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { PasswordInput } from "@/components/ui/password-input";
import { cn } from "@/lib/utils";
import { useI18n } from "@/hooks/useI18n";
import { Settings, Bot, Server } from "lucide-react";

// ============== 类型定义 ==============

export interface AgentMetadata {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  tags: string[];
}

// ============== 预定义数据 ==============

// 智能体列表
export const AGENTS_LIST: AgentMetadata[] = [
  {
    id: "text2sql_agent",
    name: "Text2SQL 智能体",
    description: "自然语言转SQL查询，支持多轮对话、Schema分析、SQL生成与执行",
    icon: "🗄️",
    category: "数据分析",
    tags: ["SQL", "数据库", "自然语言"],
  },
  {
    id: "text2testcase_agent",
    name: "测试用例生成",
    description: "根据需求自动生成测试用例，支持需求分析、测试点设计、用例编写",
    icon: "🧪",
    category: "测试工具",
    tags: ["测试用例", "自动化"],
  },
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
const AGENT_CATEGORIES = ["全部", "数据分析", "测试工具"];

// ============== Tab 类型 ==============
type TabType = "agent" | "connection";

// ============== 主组件 ==============

interface UnifiedSettingsProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  // 智能体
  currentAgentId: string;
  onAgentSelect: (agentId: string) => void;
  // 连接设置
  currentApiUrl: string;
  currentApiKey: string;
  onConnectionSave: (apiUrl: string, apiKey: string) => void;
}

export function UnifiedSettings({
  open,
  onOpenChange,
  currentAgentId,
  onAgentSelect,
  currentApiUrl,
  currentApiKey,
  onConnectionSave,
}: UnifiedSettingsProps) {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState<TabType>("agent");
  
  // 智能体筛选
  const [agentCategory, setAgentCategory] = useState("全部");
  const [agentSearch, setAgentSearch] = useState("");
  
  // 连接设置表单
  const [apiUrl, setApiUrl] = useState(currentApiUrl);
  const [apiKey, setApiKey] = useState(currentApiKey);

  // 过滤智能体
  const filteredAgents = useMemo(() => {
    return AGENTS_LIST.filter((agent) => {
      const matchCategory = agentCategory === "全部" || agent.category === agentCategory;
      const matchSearch = agentSearch === "" ||
        agent.name.toLowerCase().includes(agentSearch.toLowerCase()) ||
        agent.description.toLowerCase().includes(agentSearch.toLowerCase()) ||
        agent.tags.some((tag) => tag.toLowerCase().includes(agentSearch.toLowerCase()));
      return matchCategory && matchSearch;
    });
  }, [agentCategory, agentSearch]);

  // 按分类分组
  const groupedAgents = useMemo(() => {
    return filteredAgents.reduce((acc, agent) => {
      if (!acc[agent.category]) {
        acc[agent.category] = [];
      }
      acc[agent.category].push(agent);
      return acc;
    }, {} as Record<string, AgentMetadata[]>);
  }, [filteredAgents]);

  const handleAgentSelect = (agentId: string) => {
    onAgentSelect(agentId);
    onOpenChange(false);
  };

  const handleConnectionSave = () => {
    onConnectionSave(apiUrl, apiKey);
    onOpenChange(false);
  };

  const tabs = [
    { id: "agent" as TabType, label: "智能体", icon: Bot },
    { id: "connection" as TabType, label: "连接", icon: Server },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-hidden flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            设置
          </DialogTitle>
        </DialogHeader>

        {/* Tab 导航 */}
        <div className="flex border-b px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors",
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab 内容 */}
        <div className="flex-1 overflow-hidden">
          {/* 智能体选择 */}
          {activeTab === "agent" && (
            <div className="flex flex-col h-full">
              {/* 搜索和分类 */}
              <div className="flex flex-col gap-3 p-4 border-b">
                <input
                  type="text"
                  placeholder="搜索智能体..."
                  value={agentSearch}
                  onChange={(e) => setAgentSearch(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <div className="flex gap-2 flex-wrap">
                  {AGENT_CATEGORIES.map((category) => (
                    <Button
                      key={category}
                      variant={agentCategory === category ? "default" : "outline"}
                      size="sm"
                      onClick={() => setAgentCategory(category)}
                      className="text-xs"
                    >
                      {category}
                    </Button>
                  ))}
                </div>
              </div>

              {/* 智能体列表 */}
              <div className="flex-1 overflow-y-auto p-4">
                {Object.entries(groupedAgents).map(([category, agents]) => (
                  <div key={category} className="mb-4">
                    <h3 className="text-sm font-medium text-muted-foreground mb-2">
                      {category}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {agents.map((agent) => (
                        <AgentCard
                          key={agent.id}
                          agent={agent}
                          isSelected={agent.id === currentAgentId}
                          onSelect={() => handleAgentSelect(agent.id)}
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
            </div>
          )}

          {/* 连接设置 */}
          {activeTab === "connection" && (
            <div className="p-6 overflow-y-auto h-full">
              <div className="flex flex-col gap-6 max-w-lg">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="apiUrl">
                    {t("config.deploymentUrl")}
                    <span className="text-rose-500">{t("config.required")}</span>
                  </Label>
                  <p className="text-muted-foreground text-sm">
                    {t("config.deploymentUrlDesc")}
                  </p>
                  <Input
                    id="apiUrl"
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    placeholder="http://localhost:2024"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <Label htmlFor="apiKey">{t("config.apiKey")}</Label>
                  <p className="text-muted-foreground text-sm">
                    {t("config.apiKeyDesc")}
                  </p>
                  <PasswordInput
                    id="apiKey"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder={t("config.apiKeyPlaceholder")}
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <Button variant="outline" onClick={() => onOpenChange(false)}>
                    {t("common.cancel")}
                  </Button>
                  <Button onClick={handleConnectionSave}>{t("common.save")}</Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// ============== 智能体卡片 ==============

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
              <span key={tag} className="text-xs px-1.5 py-0.5 bg-muted rounded">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============== 快速切换按钮 ==============

interface SettingsSwitchButtonProps {
  currentAgentId: string;
  onClick: () => void;
}

export function SettingsSwitchButton({
  currentAgentId,
  onClick,
}: SettingsSwitchButtonProps) {
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

export default UnifiedSettings;
