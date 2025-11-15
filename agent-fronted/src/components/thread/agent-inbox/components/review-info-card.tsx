import { AlertCircle, Info, CheckCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ReviewInfo {
  title: string;
  description: string;
  severity?: "info" | "warning" | "error" | "success";
  details?: Record<string, string>;
}

interface ReviewInfoCardProps {
  info: ReviewInfo;
  className?: string;
}

/**
 * 审核信息卡片组件
 * 显示HITL中断的详细信息和上下文
 */
export function ReviewInfoCard({ info, className }: ReviewInfoCardProps) {
  const getIcon = () => {
    switch (info.severity) {
      case "warning":
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case "error":
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getBackgroundColor = () => {
    switch (info.severity) {
      case "warning":
        return "bg-yellow-50 border-yellow-200";
      case "error":
        return "bg-red-50 border-red-200";
      case "success":
        return "bg-green-50 border-green-200";
      default:
        return "bg-blue-50 border-blue-200";
    }
  };

  const getAccentColor = () => {
    switch (info.severity) {
      case "warning":
        return "from-yellow-100 to-yellow-50";
      case "error":
        return "from-red-100 to-red-50";
      case "success":
        return "from-green-100 to-green-50";
      default:
        return "from-blue-100 to-blue-50";
    }
  };

  return (
    <div
      className={cn(
        "w-full rounded-lg border-2 overflow-hidden",
        getBackgroundColor(),
        className
      )}
    >
      {/* 头部 */}
      <div className={cn("bg-gradient-to-r", getAccentColor(), "px-4 py-3")}>
        <div className="flex items-start gap-3">
          {getIcon()}
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">{info.title}</h3>
            <p className="text-sm text-gray-700 mt-1">{info.description}</p>
          </div>
        </div>
      </div>

      {/* 详细信息 */}
      {info.details && Object.keys(info.details).length > 0 && (
        <div className="px-4 py-3 border-t-2 border-current border-opacity-10">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.entries(info.details).map(([key, value]) => (
              <div key={key} className="text-sm">
                <p className="font-medium text-gray-700">{key}</p>
                <p className="text-gray-600 mt-1 break-words">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
