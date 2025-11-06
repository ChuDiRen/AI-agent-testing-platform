import { useState } from "react";
import { Copy, Check, Zap, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface ToolCallDisplayProps {
  toolName: string;
  args: Record<string, any>;
  result?: any;
  error?: string;
  status?: "pending" | "running" | "success" | "error";
  attemptNumber?: number;
  className?: string;
}

export function ToolCallDisplay({
  toolName,
  args,
  result,
  error,
  status = "success",
  attemptNumber,
  className,
}: ToolCallDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  // 复制到剪贴板
  const copyToClipboard = (text: string, section: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  // 格式化JSON
  const formatJson = (obj: any): string => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  };

  // 状态样式映射
  const statusConfig = {
    pending: { bg: "bg-yellow-50", border: "border-yellow-200", icon: "text-yellow-600", label: "待处理" },
    running: { bg: "bg-blue-50", border: "border-blue-200", icon: "text-blue-600", label: "运行中" },
    success: { bg: "bg-green-50", border: "border-green-200", icon: "text-green-600", label: "成功" },
    error: { bg: "bg-red-50", border: "border-red-200", icon: "text-red-600", label: "错误" },
  };

  const config = statusConfig[status];
  const argsJson = formatJson(args);
  const resultJson = result ? formatJson(result) : null;

  return (
    <div className={cn("w-full max-w-xl overflow-hidden", className)}>
      <div className={cn(
        "w-full rounded-xl border-2 overflow-hidden shadow-md transition-all duration-200",
        config.border,
        config.bg,
        !isExpanded && "h-[76px]"
      )}>
        {/* Header - 始终显示 */}
        <div
          className={cn(
            "flex items-center justify-between gap-4 px-6 cursor-pointer hover:bg-white/30 transition-colors h-[76px]",
            isExpanded && "border-b",
            isExpanded && config.border
          )}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <Zap className={cn("h-6 w-6 shrink-0", config.icon)} />
            <div className="min-w-0 flex-1 overflow-hidden">
              <div className="flex items-baseline gap-2">
                <h3 className="text-base font-semibold text-gray-900 truncate">
                  {toolName}
                </h3>
                {attemptNumber && attemptNumber > 1 && (
                  <span className="text-xs font-normal text-gray-500 whitespace-nowrap shrink-0">
                    (第{attemptNumber}次尝试)
                  </span>
                )}
              </div>
              <p className={cn("text-sm font-medium truncate", config.icon)}>
                {attemptNumber && attemptNumber > 1 && (status === "pending" || status === "running") ? "优化重试中" : config.label}
              </p>
            </div>
          </div>
          <button
            className={cn(
              "shrink-0 rounded-lg p-2 transition-all duration-200",
              "hover:bg-white/50 active:scale-95"
            )}
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            <svg
              className={cn(
                "h-5 w-5 transition-transform duration-300",
                isExpanded && "rotate-180"
              )}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>
        </div>

        {/* 详情区域 - 可折叠（包含参数和结果） */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              {/* Args Section */}
              <div className="bg-white/70 px-6 py-5 border-b-2 border-inherit">
                <div className="flex items-center justify-between gap-3 mb-4">
                  <p className="text-sm font-semibold text-gray-800 uppercase tracking-wider">
                    参数
                  </p>
                  <button
                    onClick={() => copyToClipboard(argsJson, "args")}
                    className="p-2 rounded-lg hover:bg-white/80 transition-all duration-200 shrink-0 shadow-sm"
                    title="复制参数"
                  >
                    {copiedSection === "args" ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4 text-gray-600" />
                    )}
                  </button>
                </div>
                <pre className="text-sm bg-white rounded-lg p-5 border-2 border-gray-200 overflow-x-auto min-h-[60px] max-h-48 overflow-y-auto font-mono text-gray-900 w-full break-words whitespace-pre-wrap leading-6 shadow-inner">
                  {argsJson}
                </pre>
              </div>

              {/* Result Section */}
              {error ? (
                <div className="bg-red-50/80 px-6 py-5 border-t-2 border-red-200">
                  <div className="flex items-start gap-4">
                    <AlertCircle className="h-6 w-6 text-red-600 shrink-0 mt-1" />
                    <div className="flex-1 min-w-0">
                      <p className="text-base font-semibold text-red-900 mb-4">错误</p>
                      <pre className="text-sm bg-white rounded-lg p-5 border-2 border-red-200 overflow-x-auto min-h-[60px] max-h-64 overflow-y-auto font-mono text-red-900 w-full break-words whitespace-pre-wrap leading-6 shadow-inner scrollbar-thin scrollbar-thumb-red-300 scrollbar-track-red-100">
                        {error}
                      </pre>
                    </div>
                  </div>
                </div>
              ) : resultJson ? (
                <div className="bg-green-50/80 px-6 py-5 border-t-2 border-green-200">
                  <div className="flex items-center justify-between gap-3 mb-4">
                    <p className="text-sm font-semibold text-green-800 uppercase tracking-wider">
                      结果
                    </p>
                    <button
                      onClick={() => copyToClipboard(resultJson, "result")}
                      className="p-2 rounded-lg hover:bg-white/80 transition-all duration-200 shrink-0 shadow-sm"
                      title="复制结果"
                    >
                      {copiedSection === "result" ? (
                        <Check className="h-4 w-4 text-green-700" />
                      ) : (
                        <Copy className="h-4 w-4 text-green-700" />
                      )}
                    </button>
                  </div>
                  <pre className="text-sm bg-white rounded-lg p-5 border-2 border-green-200 overflow-x-auto min-h-[80px] max-h-80 overflow-y-auto font-mono text-gray-900 w-full break-words whitespace-pre-wrap leading-6 shadow-inner scrollbar-thin scrollbar-thumb-green-300 scrollbar-track-green-100">
                    {resultJson}
                  </pre>
                </div>
              ) : (
                <div className="bg-gray-50/80 px-6 py-8 border-t-2 border-gray-200">
                  <p className="text-sm text-gray-600 text-center font-medium">无结果</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

