import { ReviewInfoCard, ReviewInfo } from "./review-info-card";
import { SqlQueryViewer } from "./sql-query-viewer";
import useInterruptedActions from "../hooks/use-interrupted-actions";
import { HumanInterrupt } from "@langchain/langgraph/prebuilt";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Loader2, ThumbsUp, XCircle, Edit2 } from "lucide-react";

interface ThreadActionsViewProps {
  interrupt: HumanInterrupt;
  handleShowSidePanel: (showState: boolean, showDescription: boolean) => void;
  showState: boolean;
  showDescription: boolean;
}

export function ThreadActionsView({
  interrupt,
  handleShowSidePanel,
  showDescription,
  showState,
}: ThreadActionsViewProps) {
  const [showEditPanel, setShowEditPanel] = useState(false);
  const [editedQuery, setEditedQuery] = useState("");

  const {
    streaming,
    streamFinished,
    loading,
    handleSubmit,
    setSelectedSubmitType,
    humanResponse,
    setHumanResponse,
    humanResponseRef,
    interruptState,
    phaseInfo,
  } = useInterruptedActions({
    interrupt,
  });

  // 提取操作信息
  const anyInt: any = interrupt as any;
  const firstAction = Array.isArray(anyInt.action_requests) && anyInt.action_requests.length > 0
    ? anyInt.action_requests[0]
    : undefined;

  const actionName = firstAction?.action || firstAction?.name || "Unknown";
  const actionArgs = firstAction?.args || {};
  const decisions: string[] = Array.isArray(anyInt.review_configs)
    ? (anyInt.review_configs[0]?.allowed_decisions ?? [])
    : [];

  const cfg = {
    allow_accept: decisions.includes("approve") || decisions.includes("accept"),
    allow_edit: decisions.includes("edit"),
    allow_ignore: decisions.includes("reject") || decisions.includes("ignore"),
    allow_respond: decisions.includes("respond") || decisions.includes("response"),
  };

  // 构建审核信息卡片数据
  const reviewInfo: ReviewInfo = {
    title: "人机协同审核",
    description: interrupt.description || "等待您的审核...",
    severity: "info",
    details: {
      "操作": actionName,
      "状态": phaseInfo.message || "处理中",
    },
  };

  // 处理批准
  const handleApprove = async () => {
    try {
      await handleSubmit(new MouseEvent("click") as any, "accept");
    } catch (error) {
      console.error("批准操作失败:", error);
    }
  };

  // 处理编辑
  const handleEdit = () => {
    setEditedQuery(sqlQuery);
    setShowEditPanel(true);
    setSelectedSubmitType("edit");
  };

  // 提交编辑
  const handleSubmitEdit = async () => {
    // 先构建更新后的数据
    const updated = humanResponse.map((p) => {
      if (p.type === "edit" && typeof p.args === "object" && p.args) {
        return {
          ...p,
          args: {
            ...p.args,
            args: {
              ...p.args.args,
              query: editedQuery,
            },
          },
        };
      }
      return p;
    });

    // 立即更新 ref（不依赖 setState 的回调）
    humanResponseRef.current = updated;

    // 更新 state
    setHumanResponse(updated);

    try {
      await handleSubmit(new MouseEvent("click") as any, "edit");
      setShowEditPanel(false);
    } catch (error) {
      console.error("提交编辑失败:", error);
    }
  };

  // 处理拒绝
  const handleReject = async () => {
    try {
      await handleSubmit(new MouseEvent("click") as any, "ignore");
    } catch (error) {
      console.error("拒绝操作失败:", error);
    }
  };

  // SQL查询信息
  const sqlQuery = actionArgs.query || "";

  return (
    <div className="w-full space-y-4">
      {/* 审核信息卡片 */}
      <ReviewInfoCard info={reviewInfo} />

      {/* SQL查询查看器 */}
      {sqlQuery && !showEditPanel && (
        <SqlQueryViewer
          query={sqlQuery}
          title="SQL 查询"
          editable={false}
        />
      )}

      {/* 编辑面板 */}
      {showEditPanel && sqlQuery && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 space-y-4">
          <div className="flex items-center gap-2">
            <Edit2 className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">编辑模式</h3>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">SQL 查询</label>
            <textarea
              value={editedQuery}
              onChange={(e) => setEditedQuery(e.target.value)}
              disabled={streaming}
              className="w-full h-48 p-3 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              spellCheck="false"
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={() => {
                setShowEditPanel(false);
                setEditedQuery("");
              }}
              disabled={streaming}
            >
              取消
            </Button>
            <Button
              onClick={handleSubmitEdit}
              disabled={streaming}
              className="bg-blue-600 hover:bg-blue-700"
            >
              提交修改
            </Button>
          </div>
        </div>
      )}

      {/* 决策按钮组 */}
      {!showEditPanel && (
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-3">
          {cfg.allow_accept && (
            <Button
              onClick={handleApprove}
              disabled={loading || streaming}
              variant="outline"
              className="gap-2"
            >
              <ThumbsUp className="w-4 h-4" />
              <span className="hidden sm:inline">批准</span>
            </Button>
          )}

          {cfg.allow_edit && (
            <Button
              onClick={handleEdit}
              disabled={loading || streaming}
              variant="outline"
              className="gap-2"
            >
              <Edit2 className="w-4 h-4" />
              <span className="hidden sm:inline">编辑</span>
            </Button>
          )}

          {cfg.allow_ignore && (
            <Button
              onClick={handleReject}
              disabled={loading || streaming}
              variant="outline"
              className="gap-2"
            >
              <XCircle className="w-4 h-4" />
              <span className="hidden sm:inline">拒绝</span>
            </Button>
          )}
        </div>
      )}

      {/* 执行状态 */}
      {streaming && (
        <div className="flex items-center justify-center gap-2 rounded-lg bg-yellow-50 p-3 border border-yellow-200">
          <Loader2 className="h-4 w-4 animate-spin text-yellow-600" />
          <p className="text-sm font-medium text-yellow-700">执行中...</p>
        </div>
      )}

      {streamFinished && (
        <div className="flex items-center justify-center gap-2 rounded-lg bg-green-50 p-3 border border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <p className="text-sm font-medium text-green-600">执行完成</p>
        </div>
      )}
    </div>
  );
}
