import { Button } from "@/components/ui/button";
import { InboxItemInput } from "./inbox-item-input";
import useInterruptedActions from "../hooks/use-interrupted-actions";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useQueryState } from "nuqs";
import { constructOpenInStudioURL } from "../utils";
import { HumanInterrupt } from "@langchain/langgraph/prebuilt";
import { UnifiedCard } from "@/components/ui/unified-card";

interface ThreadActionsViewProps {
  interrupt: HumanInterrupt;
  handleShowSidePanel: (showState: boolean, showDescription: boolean) => void;
  showState: boolean;
  showDescription: boolean;
}

// 移除状态/说明切换与线程ID展示，简化为仅标题

export function ThreadActionsView({
  interrupt,
  handleShowSidePanel,
  showDescription,
  showState,
}: ThreadActionsViewProps) {
  // 不展示线程ID
  const {
    acceptAllowed,
    hasEdited,
    hasAddedResponse,
    streaming,
    supportsMultipleMethods,
    streamFinished,
    loading,
    handleSubmit,
    handleIgnore,
    handleResolve,
    handleContinue, // 新增：继续处理函数
    setSelectedSubmitType,
    setHasAddedResponse,
    setHasEdited,
    humanResponse,
    setHumanResponse,
    initialHumanInterruptEditValue,
    interruptState, // 新增：状态机状态
    phaseInfo, // 新增：阶段信息
    selectedSubmitType,
  } = useInterruptedActions({
    interrupt,
  });
  const [apiUrl] = useQueryState("apiUrl");

  const handleOpenInStudio = () => { };

  // Title fallback: support legacy action_request and modern action_requests
  const anyIntForTitle: any = interrupt as any;
  const firstActionForTitle = (Array.isArray(anyIntForTitle.action_requests) && anyIntForTitle.action_requests.length > 0
    ? anyIntForTitle.action_requests[0]
    : undefined);
  const threadTitle = firstActionForTitle?.action || firstActionForTitle?.name || "Unknown";
  const actionsDisabled = loading || streaming;
  // Normalize ignoreAllowed from legacy config or modern review_configs
  const anyInt: any = interrupt as any;
  const decisions: string[] = Array.isArray(anyInt.review_configs)
    ? (anyInt.review_configs[0]?.allowed_decisions ?? [])
    : [];
  const ignoreAllowed = decisions.includes("reject") || decisions.includes("ignore");

  const cardHeader = (
    <div className="flex w-full flex-col gap-2">
      <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">{threadTitle}</h1>
    </div>
  );

  return (
    <UnifiedCard variant="default" size="md" className="w-full" header={cardHeader}>
      <div className="flex w-full flex-col gap-4">
        {/* Action Buttons # 响应式按钮组 */}
        <div className="flex w-full flex-col gap-2 sm:flex-row sm:items-center">
          <Button
            variant={selectedSubmitType === "ignore" ? "outline" : "brand"}
            className="font-normal"
            onClick={() => setSelectedSubmitType(acceptAllowed ? "accept" : "edit")}
            disabled={actionsDisabled}
          >
            同意
          </Button>
          {ignoreAllowed && (
            <Button
              variant={selectedSubmitType === "ignore" ? "destructive" : "outline"}
              className="border-gray-500 bg-white font-normal text-gray-800"
              onClick={() => setSelectedSubmitType("ignore")}
              disabled={actionsDisabled}
            >
              拒绝
            </Button>
          )}
        </div>

        {/* Actions # 主要内容区域 */}
        <InboxItemInput
          acceptAllowed={acceptAllowed}
          hasEdited={hasEdited}
          hasAddedResponse={hasAddedResponse}
          interruptValue={interrupt}
          humanResponse={humanResponse}
          initialValues={initialHumanInterruptEditValue.current}
          setHumanResponse={setHumanResponse}
          streaming={streaming}
          streamFinished={streamFinished}
          supportsMultipleMethods={supportsMultipleMethods}
          phaseInfo={phaseInfo} // 新增：传入阶段信息
          selectedSubmitType={selectedSubmitType}
          setSelectedSubmitType={setSelectedSubmitType}
          setHasAddedResponse={setHasAddedResponse}
          setHasEdited={setHasEdited}
          handleSubmit={handleSubmit}
        />

        {/* 继续按钮 # 在resumed状态显示 */}
        {phaseInfo.showContinue && (
          <div className="mx-auto w-full max-w-2xl">
            <Button
              onClick={handleContinue}
              variant="brand"
              className="w-full"
            >
              继续处理
            </Button>
          </div>
        )}
      </div>
    </UnifiedCard>
  );
}
