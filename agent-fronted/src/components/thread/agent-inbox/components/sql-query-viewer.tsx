import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Copy, Copy as CopyIcon, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface SqlQueryViewerProps {
  query: string;
  title?: string;
  editable?: boolean;
  onChange?: (value: string) => void;
}

/**
 * SQL查询查看器组件
 * 提供SQL语法高亮、格式化和复制功能
 */
export function SqlQueryViewer({
  query,
  title = "Query",
  editable = false,
  onChange,
}: SqlQueryViewerProps) {
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(query);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(query);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = () => {
    onChange?.(editValue);
    setIsEditing(false);
  };

  const formatSql = (sql: string) => {
    // 基础SQL格式化
    return sql
      .replace(/\s+/g, " ")
      .replace(/\b(SELECT|FROM|WHERE|JOIN|ON|GROUP BY|ORDER BY|LIMIT|HAVING|UNION|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b/gi, "\n$1")
      .trim();
  };

  return (
    <div className="w-full rounded-lg border border-gray-200 bg-gray-50 overflow-hidden">
      {/* 头部 */}
      <div className="flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <h3 className="font-semibold text-gray-700">{title}</h3>
        </div>
        <div className="flex items-center gap-2">
          {editable && (
            <Button
              size="sm"
              variant={isEditing ? "default" : "outline"}
              onClick={() => setIsEditing(!isEditing)}
              className="text-xs"
            >
              {isEditing ? "完成编辑" : "编辑"}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={handleCopy}
            className="text-xs gap-1"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3" />
                已复制
              </>
            ) : (
              <>
                <CopyIcon className="w-3 h-3" />
                复制
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 内容区域 */}
      <div className="p-4">
        {isEditing ? (
          <div className="space-y-3">
            <textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="w-full h-48 p-3 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              spellCheck="false"
            />
            <div className="flex gap-2 justify-end">
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  setEditValue(query);
                }}
              >
                取消
              </Button>
              <Button size="sm" onClick={handleSave} className="bg-blue-600 hover:bg-blue-700">
                保存修改
              </Button>
            </div>
          </div>
        ) : (
          <pre className="font-mono text-sm text-gray-700 overflow-x-auto whitespace-pre-wrap break-words leading-relaxed">
            <code>{formatSql(query)}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
