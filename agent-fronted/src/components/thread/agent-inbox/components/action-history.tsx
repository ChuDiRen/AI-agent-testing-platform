import { useState } from "react";
import { ChevronDown, ChevronUp, Clock, CheckCircle, AlertCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ActionLog {
  id: string;
  timestamp: Date;
  action: string;
  status: "pending" | "success" | "error" | "warning";
  message: string;
  details?: Record<string, any>;
}

interface ActionHistoryProps {
  logs: ActionLog[];
  maxHeight?: string;
}

/**
 * 操作历史和日志组件
 * 显示HITL工作流中的所有操作和状态变化
 */
export function ActionHistory({ logs, maxHeight = "max-h-64" }: ActionHistoryProps) {
  const [expanded, setExpanded] = useState(false);
  const [expandedLogs, setExpandedLogs] = useState<Set<string>>(new Set());

  const toggleLogExpanded = (id: string) => {
    const newSet = new Set(expandedLogs);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedLogs(newSet);
  };

  const getStatusIcon = (status: ActionLog["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "error":
        return <XCircle className="w-4 h-4 text-red-500" />;
      case "warning":
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case "pending":
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = (status: ActionLog["status"]) => {
    switch (status) {
      case "success":
        return "bg-green-50 border-green-200";
      case "error":
        return "bg-red-50 border-red-200";
      case "warning":
        return "bg-yellow-50 border-yellow-200";
      case "pending":
        return "bg-blue-50 border-blue-200";
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  if (logs.length === 0) {
    return null;
  }

  return (
    <div className="w-full rounded-lg border border-gray-200 bg-white overflow-hidden">
      {/* 头部 */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-600" />
          <h3 className="font-semibold text-gray-700">操作历史</h3>
          <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
            {logs.length}
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-gray-600" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-600" />
        )}
      </button>

      {/* 日志列表 */}
      {expanded && (
        <div className={`${maxHeight} overflow-y-auto`}>
          <div className="divide-y divide-gray-100">
            {logs.map((log, index) => (
              <div
                key={log.id}
                className={cn(
                  "p-3 border-l-4 transition-colors",
                  getStatusColor(log.status),
                  {
                    "border-l-green-500": log.status === "success",
                    "border-l-red-500": log.status === "error",
                    "border-l-yellow-500": log.status === "warning",
                    "border-l-blue-500": log.status === "pending",
                  }
                )}
              >
                {/* 日志头部 */}
                <button
                  onClick={() => toggleLogExpanded(log.id)}
                  className="w-full flex items-start gap-3 text-left hover:opacity-75 transition-opacity"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {getStatusIcon(log.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 justify-between">
                      <p className="font-medium text-sm text-gray-900 truncate">
                        {log.action}
                      </p>
                      <span className="text-xs text-gray-500 flex-shrink-0">
                        {formatTime(log.timestamp)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{log.message}</p>
                  </div>
                  {log.details && (
                    <div className="flex-shrink-0">
                      {expandedLogs.has(log.id) ? (
                        <ChevronUp className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  )}
                </button>

                {/* 详细信息 */}
                {log.details && expandedLogs.has(log.id) && (
                  <div className="mt-3 pl-7 pt-3 border-t border-current border-opacity-10">
                    <pre className="text-xs bg-white bg-opacity-50 p-2 rounded border border-current border-opacity-20 overflow-x-auto">
                      <code>{JSON.stringify(log.details, null, 2)}</code>
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
