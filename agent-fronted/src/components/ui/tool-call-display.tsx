import { useState } from "react";
import { Copy, Check, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { MarkdownImage } from "@/components/thread/markdown-image";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

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
  const [isExpanded, setIsExpanded] = useState(false); // 默认折叠
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const copyToClipboard = (text: string, section: string) => { // 复制到剪贴板
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const formatJson = (obj: any): string => {
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  };

  const detectLanguage = (obj: any): string => {
    // 检测是否为SQL查询
    if (typeof obj === "object" && obj !== null && "query" in obj) {
      const query = obj.query;
      if (typeof query === "string" && /^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)/i.test(query)) {
        return "sql";
      }
    }
    return "json";
  };

  const isImageUrl = (str: string): boolean => { // 检测是否是图片URL
    if (typeof str !== 'string') return false;
    const imageUrlPattern = /^https?:\/\/.+\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i;
    const imagePathPattern = /^https?:\/\/.+\/(img|image|images|afts\/img|picture|pic)\//i;
    return imageUrlPattern.test(str) || imagePathPattern.test(str);
  };

  const getImageUrlFromResult = (): string | null => { // 检测结果是否包含图片URL
    if (!result) return null;
    if (typeof result === 'string' && isImageUrl(result)) return result;
    if (typeof result === 'object' && result !== null) {
      const possibleKeys = ['image', 'imageUrl', 'image_url', 'url', 'src', 'chart', 'chartUrl', 'chart_url'];
      for (const key of possibleKeys) {
        if (result[key] && typeof result[key] === 'string' && isImageUrl(result[key])) {
          return result[key];
        }
      }
    }
    return null;
  };

  const imageUrl = getImageUrlFromResult();
  const argsJson = formatJson(args);
  const resultJson = result ? formatJson(result) : null;
  const argsLanguage = detectLanguage(args);
  const resultLanguage = result ? detectLanguage(result) : "json";

  // 自定义样式,使用浅色主题
  const customStyle = {
    margin: 0,
    padding: "12px",
    background: "#f9fafb",
    fontSize: "12px",
    lineHeight: "1.6",
    borderRadius: "6px",
    border: "1px solid #e5e7eb",
  };

  return (
    <div className={cn("w-full", className)}>
      <div className={cn(
        "w-full rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md",
        !isExpanded && "h-[52px]" // 折叠时固定高度
      )}>
        {/* Header */}
        <div
          className={cn(
            "flex items-center justify-between px-4 h-[52px] cursor-pointer select-none", // 固定header高度
            "hover:bg-gray-50 transition-colors duration-200",
            isExpanded && "border-b border-gray-200 bg-gray-50"
          )}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm font-medium text-gray-700 truncate">
                {toolName}
              </span>
              {attemptNumber && attemptNumber > 1 && (
                <span className="text-xs text-gray-500 whitespace-nowrap shrink-0">
                  (尝试 {attemptNumber})
                </span>
              )}
            </div>
          </div>
          <button
            className={cn(
              "shrink-0 p-1 rounded transition-transform duration-300",
              isExpanded && "rotate-180"
            )}
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            <ChevronDown className="h-4 w-4 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
              className="overflow-hidden"
            >
              <div className="px-4 py-3 space-y-3">
                {/* Args */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-gray-600 uppercase">参数</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(argsJson, "args");
                      }}
                      className="p-1.5 rounded hover:bg-gray-100 transition-colors"
                      title="复制参数"
                    >
                      {copiedSection === "args" ? (
                        <Check className="h-3.5 w-3.5 text-green-600" />
                      ) : (
                        <Copy className="h-3.5 w-3.5 text-gray-500" />
                      )}
                    </button>
                  </div>
                  <div className="max-h-60 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
                    <SyntaxHighlighter
                      language={argsLanguage}
                      style={vscDarkPlus}
                      customStyle={customStyle}
                      showLineNumbers={false}
                      wrapLines={true}
                      wrapLongLines={true}
                    >
                      {argsJson}
                    </SyntaxHighlighter>
                  </div>
                </div>

                {/* Result */}
                {error ? (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-semibold text-red-600 uppercase">错误</span>
                    </div>
                    <pre className="text-xs bg-red-50 rounded border border-red-200 p-3 overflow-x-auto max-h-60 overflow-y-auto font-mono text-red-800 whitespace-pre-wrap break-words scrollbar-thin scrollbar-thumb-red-300 scrollbar-track-transparent">
                      {error}
                    </pre>
                  </div>
                ) : result ? (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold text-gray-600 uppercase">结果</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(resultJson!, "result");
                        }}
                        className="p-1.5 rounded hover:bg-gray-100 transition-colors"
                        title="复制结果"
                      >
                        {copiedSection === "result" ? (
                          <Check className="h-3.5 w-3.5 text-green-600" />
                        ) : (
                          <Copy className="h-3.5 w-3.5 text-gray-500" />
                        )}
                      </button>
                    </div>
                    {imageUrl ? (
                      <div className="bg-gray-50 rounded border border-gray-200 p-3">
                        <MarkdownImage src={imageUrl} alt="生成的图表" />
                      </div>
                    ) : (
                      <div className="max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
                        <SyntaxHighlighter
                          language={resultLanguage}
                          style={vscDarkPlus}
                          customStyle={customStyle}
                          showLineNumbers={false}
                          wrapLines={true}
                          wrapLongLines={true}
                        >
                          {resultJson!}
                        </SyntaxHighlighter>
                      </div>
                    )}
                  </div>
                ) : null}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

