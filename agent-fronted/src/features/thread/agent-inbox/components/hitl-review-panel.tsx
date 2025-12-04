import { HumanInterrupt } from "@langchain/langgraph/prebuilt";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { AlertCircle, CheckCircle, Edit2, XCircle, ThumbsUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface HITLReviewPanelProps {
  interrupt: HumanInterrupt;
  onApprove?: () => void;
  onReject?: () => void;
  onEdit?: () => void;
  onRespond?: () => void;
  loading?: boolean;
}

/**
 * HITL审核面板组件
 * 提供清晰的人机协同决策界面
 */
export function HITLReviewPanel({
  interrupt,
  onApprove,
  onReject,
  onEdit,
  onRespond,
  loading = false,
}: HITLReviewPanelProps) {
  const anyInt: any = interrupt as any;
  const firstAction = Array.isArray(anyInt.action_requests) && anyInt.action_requests.length > 0
    ? anyInt.action_requests[0]
    : undefined;

  const actionName = firstAction?.action || firstAction?.name || "Unknown";
  const actionArgs = firstAction?.args || {};
  const description = interrupt.description || "等待您的审核...";

  // 获取允许的决策
  const decisions: string[] = Array.isArray(anyInt.review_configs)
    ? (anyInt.review_configs[0]?.allowed_decisions ?? [])
    : [];

  const allowApprove = decisions.includes("approve") || decisions.includes("accept");
  const allowEdit = decisions.includes("edit");
  const allowReject = decisions.includes("reject") || decisions.includes("ignore");
  const allowRespond = decisions.includes("respond") || decisions.includes("response");

  return (
    <div className="w-full space-y-4">
      {/* 头部：操作信息 */}
      <div className="rounded-lg bg-white border border-gray-200 shadow-sm p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">人机协同审核 <span className="text-orange-500">●</span></h3>
            <p className="text-sm text-gray-700 mt-1">
              <span className="font-medium">操作：</span>{actionName}
            </p>
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          </div>
        </div>
      </div>

      {/* 操作详情卡片 */}
      <Card className="p-4 border-gray-200">
        <div className="space-y-3">
          {/* 操作参数 */}
          {Object.keys(actionArgs).length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">操作参数</h4>
              <div className="bg-gray-50 rounded p-3 text-sm font-mono text-gray-700 max-h-48 overflow-y-auto">
                {Object.entries(actionArgs).map(([key, value]) => (
                  <div key={key} className="mb-2">
                    <span className="text-blue-600">{key}:</span>{" "}
                    <span className="text-gray-800">
                      {typeof value === "string" ? value : JSON.stringify(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* 决策按钮组 */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {allowApprove && (
          <Button
            onClick={onApprove}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white gap-2"
          >
            <ThumbsUp className="w-4 h-4" />
            <span className="hidden sm:inline">批准</span>
          </Button>
        )}

        {allowEdit && (
          <Button
            onClick={onEdit}
            disabled={loading}
            variant="outline"
            className="gap-2"
          >
            <Edit2 className="w-4 h-4" />
            <span className="hidden sm:inline">编辑</span>
          </Button>
        )}

        {allowRespond && (
          <Button
            onClick={onRespond}
            disabled={loading}
            variant="outline"
            className="gap-2"
          >
            <span className="hidden sm:inline">自定义</span>
          </Button>
        )}

        {allowReject && (
          <Button
            onClick={onReject}
            disabled={loading}
            variant="destructive"
            className="gap-2"
          >
            <XCircle className="w-4 h-4" />
            <span className="hidden sm:inline">拒绝</span>
          </Button>
        )}
      </div>

      {/* 决策说明 */}
      <div className="rounded-lg bg-gray-50 border border-gray-200 p-3 text-sm text-gray-700">
        <p className="font-medium mb-1">💡 决策说明</p>
        <ul className="space-y-1 text-xs">
          {allowApprove && <li>• <strong>批准</strong>：直接执行此操作</li>}
          {allowEdit && <li>• <strong>编辑</strong>：修改参数后执行</li>}
          {allowRespond && <li>• <strong>自定义</strong>：提供自定义响应</li>}
          {allowReject && <li>• <strong>拒绝</strong>：中止此操作</li>}
        </ul>
      </div>
    </div>
  );
}
