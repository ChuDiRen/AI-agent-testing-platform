import { HumanResponseWithEdits, SubmitType, InterruptPhaseInfo } from "../types";
import { Textarea } from "@/components/ui/textarea";
import React from "react";
import { haveArgsChanged, prettifyText } from "../utils";
import { Button } from "@/components/ui/button";
import { Undo2, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { MarkdownText } from "../../markdown-text";
import { ActionRequest, HumanInterrupt } from "@langchain/langgraph/prebuilt";
import { toast } from "sonner";
// removed Separator import (no multi-method divider)
import { cn } from "@/lib/utils";
import { UnifiedCard, CardContainer } from "@/components/ui/unified-card"; // 新增：统一卡片组件

// 阶段状态显示组件 # UI反馈组件
function PhaseStatusBadge({ phaseInfo }: { phaseInfo: InterruptPhaseInfo }) {
  if (!phaseInfo.message) return null;

  const getStatusIcon = () => {
    switch (phaseInfo.state) {
      case "interrupted":
      case "responding":
        return <AlertCircle className="h-4 w-4" />;
      case "submitting":
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case "resumed":
      case "completed":
        return <CheckCircle2 className="h-4 w-4" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = () => {
    switch (phaseInfo.state) {
      case "interrupted":
      case "responding":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "submitting":
      case "processing":
        return "bg-yellow-50 text-yellow-700 border-yellow-200";
      case "resumed":
      case "completed":
        return "bg-green-50 text-green-700 border-green-200";
      case "error":
        return "bg-red-50 text-red-700 border-red-200";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200";
    }
  };

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium",
        getStatusColor()
      )}
    >
      {getStatusIcon()}
      <span>{phaseInfo.message}</span>
    </div>
  );
}

function ResetButton({ handleReset }: { handleReset: () => void }) {
  return (
    <Button
      onClick={handleReset}
      variant="ghost"
      className="flex items-center justify-center gap-2 text-gray-500 hover:text-red-500"
    >
      <Undo2 className="h-4 w-4" />
      <span>重置</span>
    </Button>
  );
}

function ArgsRenderer({ args }: { args: Record<string, any> }) {
  return (
    <div className="flex w-full flex-col items-start gap-4">
      {Object.entries(args).map(([k, v]) => {
        let value = "";
        if (["string", "number"].includes(typeof v)) {
          value = v.toString();
        } else {
          value = JSON.stringify(v, null, 2);
        }

        const label = k === "query" ? "SQL 查询" : prettifyText(k);

        return (
          <div
            key={`args-${k}`}
            className="flex flex-col items-start gap-2"
          >
            <p className="text-sm font-medium text-gray-700">
              {label}:
            </p>
            <div className="w-full rounded-lg bg-gray-50 p-3 border border-gray-200">
              <MarkdownText>{value}</MarkdownText>
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface InboxItemInputProps {
  interruptValue: HumanInterrupt;
  humanResponse: HumanResponseWithEdits[];
  supportsMultipleMethods: boolean;
  acceptAllowed: boolean;
  hasEdited: boolean;
  hasAddedResponse: boolean;
  initialValues: Record<string, string>;

  streaming: boolean;
  streamFinished: boolean;
  phaseInfo: InterruptPhaseInfo; // 新增：阶段信息
  selectedSubmitType?: SubmitType;

  setHumanResponse: React.Dispatch<
    React.SetStateAction<HumanResponseWithEdits[]>
  >;
  setSelectedSubmitType: React.Dispatch<
    React.SetStateAction<SubmitType | undefined>
  >;
  setHasAddedResponse: React.Dispatch<React.SetStateAction<boolean>>;
  setHasEdited: React.Dispatch<React.SetStateAction<boolean>>;

  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
    submitType?: SubmitType,
  ) => Promise<void>;
}

function ResponseComponent({
  humanResponse,
  streaming,
  showArgsInResponse,
  actionRequestArgs,
  onResponseChange,
  handleSubmit,
}: {
  humanResponse: HumanResponseWithEdits[];
  streaming: boolean;
  showArgsInResponse: boolean;
  actionRequestArgs: Record<string, any>;
  onResponseChange: (change: string, response: HumanResponseWithEdits) => void;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
    submitType?: SubmitType,
  ) => Promise<void>;
}) {
  const res = humanResponse.find((r) => r.type === "response");
  if (!res || typeof res.args !== "string") {
    return null;
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <UnifiedCard variant="bordered" size="md">
      <div className="flex w-full flex-col items-start gap-4">
        <div className="flex w-full items-center justify-between">
          <p className="text-base font-semibold text-black">回复助手</p>
          <ResetButton
            handleReset={() => {
              onResponseChange("", res);
            }}
          />
        </div>

        {showArgsInResponse && (
          <ArgsRenderer args={actionRequestArgs} />
        )}

        <div className="flex w-full flex-col items-start gap-2">
          <p className="min-w-fit text-sm font-medium">回复</p>
          <Textarea
            disabled={streaming}
            value={res.args}
            onChange={(e) => onResponseChange(e.target.value, res)}
            onKeyDown={handleKeyDown}
            rows={4}
            placeholder="在此输入您的回复..."
          />
        </div>

        <div className="flex w-full items-center justify-end gap-2">
          <Button
            variant="brand"
            disabled={streaming}
            onClick={handleSubmit}
          >
            发送回复
          </Button>
        </div>
      </div>
    </UnifiedCard>
  );
}
const Response = React.memo(ResponseComponent);

function RejectComponent({
  humanResponse,
  streaming,
  onRejectChange,
  handleSubmit,
}: {
  humanResponse: HumanResponseWithEdits[];
  streaming: boolean;
  onRejectChange: (change: string, response: HumanResponseWithEdits) => void;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
    submitType?: SubmitType,
  ) => Promise<void>;
}) {
  const res = humanResponse.find((r) => r.type === "ignore");
  if (!res || typeof res.args !== "string") {
    return null;
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <UnifiedCard variant="bordered" size="md">
      <div className="flex w-full flex-col items-start gap-4">
        <div className="flex w-full items-center justify-between">
          <p className="text-base font-semibold text-black">拒绝原因</p>
          <ResetButton
            handleReset={() => {
              onRejectChange("", res);
            }}
          />
        </div>

        <div className="flex w-full flex-col items-start gap-2">
          <p className="min-w-fit text-sm font-medium">原因</p>
          <Textarea
            disabled={streaming}
            value={res.args}
            onChange={(e) => onRejectChange(e.target.value, res)}
            onKeyDown={handleKeyDown}
            rows={3}
            placeholder="简要说明拒绝原因..."
          />
          <p className="text-xs text-gray-500">必填：请简要说明拒绝的原因</p>
        </div>

        <div className="flex w-full items-center justify-end gap-2">
          <Button
            variant="destructive"
            disabled={streaming || !res.args || (typeof res.args === "string" && res.args.trim().length === 0)}
            onClick={(e) => handleSubmit(e, "ignore")}
          >
            拒绝
          </Button>
        </div>
      </div>
    </UnifiedCard>
  );
}

function AcceptComponent({
  streaming,
  actionRequestArgs,
  handleSubmit,
}: {
  streaming: boolean;
  actionRequestArgs: Record<string, any>;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
    submitType?: SubmitType,
  ) => Promise<void>;
}) {
  return (
    <UnifiedCard variant="bordered" size="md">
      <div className="flex w-full flex-col items-start gap-4">
        {actionRequestArgs && Object.keys(actionRequestArgs).length > 0 && (
          <ArgsRenderer args={actionRequestArgs} />
        )}
        <Button
          variant="brand"
          disabled={streaming}
          onClick={(e) => handleSubmit(e, "accept")}
          className="w-full"
        >
          接受
        </Button>
      </div>
    </UnifiedCard>
  );
}

function EditAndOrAcceptComponent({
  humanResponse,
  streaming,
  initialValues,
  onEditChange,
  handleSubmit,
  interruptValue,
  actionRequestArgs,
  setSelectedSubmitType,
}: {
  humanResponse: HumanResponseWithEdits[];
  streaming: boolean;
  initialValues: Record<string, string>;
  interruptValue: HumanInterrupt;
  actionRequestArgs: Record<string, any>;
  onEditChange: (
    text: string | string[],
    response: HumanResponseWithEdits,
    key: string | string[],
  ) => void;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
    submitType?: SubmitType,
  ) => Promise<void>;
  setSelectedSubmitType: React.Dispatch<React.SetStateAction<SubmitType | undefined>>;
}) {
  const defaultRows = React.useRef<Record<string, number>>({});
  const editResponse = humanResponse.find((r) => r.type === "edit");
  const acceptResponse = humanResponse.find((r) => r.type === "accept");
  if (
    !editResponse ||
    typeof editResponse.args !== "object" ||
    !editResponse.args
  ) {
    if (acceptResponse) {
      return (
        <AcceptComponent
          actionRequestArgs={actionRequestArgs}
          streaming={streaming}
          handleSubmit={handleSubmit}
        />
      );
    }
    return null;
  }
  const header = editResponse.acceptAllowed ? "编辑/接受" : "编辑";

  const handleReset = () => {
    if (
      !editResponse ||
      typeof editResponse.args !== "object" ||
      !editResponse.args ||
      !editResponse.args.args
    ) {
      return;
    }
    // use initialValues to reset the text areas
    const keysToReset: string[] = [];
    const valuesToReset: string[] = [];
    Object.entries(initialValues).forEach(([k, v]) => {
      if (k in (editResponse.args as Record<string, any>).args) {
        const value = ["string", "number"].includes(typeof v)
          ? v
          : JSON.stringify(v, null);
        keysToReset.push(k);
        valuesToReset.push(value);
      }
    });

    if (keysToReset.length > 0 && valuesToReset.length > 0) {
      onEditChange(valuesToReset, editResponse, keysToReset);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <UnifiedCard variant="bordered" size="md">
      <div className="flex w-full flex-col items-start gap-4">
        <div className="flex w-full items-center justify-between">
          <p className="text-base font-semibold text-black">{header}</p>
          <ResetButton handleReset={handleReset} />
        </div>

        {Object.entries(editResponse.args.args).map(([k, v], idx) => {
          const value = ["string", "number"].includes(typeof v)
            ? v
            : JSON.stringify(v, null);
          // Calculate the default number of rows by the total length of the initial value divided by 30
          // or 8, whichever is greater. Stored in a ref to prevent re-rendering.
          if (
            defaultRows.current[k as keyof typeof defaultRows.current] ===
            undefined
          ) {
            defaultRows.current[k as keyof typeof defaultRows.current] = !v.length
              ? 3
              : Math.max(v.length / 30, 7);
          }
          const numRows =
            defaultRows.current[k as keyof typeof defaultRows.current] || 8;

          return (
            <div
              className="flex h-full w-full flex-col items-start gap-1"
              key={`allow-edit-args--${k}-${idx}`}
            >
              <div className="flex w-full flex-col items-start gap-2">
                <p className="min-w-fit text-sm font-medium">{prettifyText(k)}</p>
                <Textarea
                  disabled={streaming}
                  className="h-full"
                  value={value}
                  onChange={(e) => onEditChange(e.target.value, editResponse, k)}
                  onKeyDown={handleKeyDown}
                  rows={numRows}
                />
              </div>
            </div>
          );
        })}

        <div className="flex w-full items-center justify-end gap-2">
          {editResponse.acceptAllowed && (
            <Button
              variant="outline"
              disabled={streaming}
              onClick={(e) => {
                setSelectedSubmitType("accept");
                handleSubmit(e, "accept");
              }}
            >
              接受执行
            </Button>
          )}
          <Button
            variant="brand"
            disabled={streaming || !editResponse.editsMade}
            onClick={(e) => {
              setSelectedSubmitType("edit");
              handleSubmit(e, "edit");
            }}
          >
            提交修改
          </Button>
        </div>
      </div>
    </UnifiedCard>
  );
}
const EditAndOrAccept = React.memo(EditAndOrAcceptComponent);

export function InboxItemInput({
  interruptValue,
  humanResponse,
  streaming,
  streamFinished,
  supportsMultipleMethods,
  acceptAllowed,
  hasEdited,
  hasAddedResponse,
  initialValues,
  phaseInfo, // 新增：阶段信息
  selectedSubmitType,
  setHumanResponse,
  setSelectedSubmitType,
  setHasEdited,
  setHasAddedResponse,
  handleSubmit,
}: InboxItemInputProps) {
  // Expect modern middleware shape
  const anyInt: any = interruptValue as any;
  const firstAction = (
    Array.isArray(anyInt.action_requests) && anyInt.action_requests.length > 0
      ? anyInt.action_requests[0]
      : undefined
  );
  const actionRequestArgs: Record<string, any> = firstAction?.args ?? {};

  const decisions: string[] = Array.isArray(anyInt.review_configs)
    ? (anyInt.review_configs[0]?.allowed_decisions ?? [])
    : [];
  const cfg = {
    allow_accept: decisions.includes("approve") || decisions.includes("accept"),
    allow_edit: decisions.includes("edit"),
    allow_ignore: decisions.includes("reject") || decisions.includes("ignore"),
    allow_respond: decisions.includes("respond") || decisions.includes("response"),
  };

  const isEditAllowed = !!cfg.allow_edit;
  const isResponseAllowed = !!cfg.allow_respond;
  const hasArgs = Object.entries(actionRequestArgs).length > 0;
  const showArgsInResponse =
    hasArgs && !isEditAllowed && !acceptAllowed && isResponseAllowed;
  const showArgsOutsideActionCards =
    hasArgs && !showArgsInResponse && !isEditAllowed && !acceptAllowed;

  const onEditChange = (
    change: string | string[],
    response: HumanResponseWithEdits,
    key: string | string[],
  ) => {
    if (
      (Array.isArray(change) && !Array.isArray(key)) ||
      (!Array.isArray(change) && Array.isArray(key))
    ) {
      toast.error("Error", {
        description: "Something went wrong",
        richColors: true,
        closeButton: true,
      });
      return;
    }

    let valuesChanged = true;
    if (typeof response.args === "object") {
      const updatedArgs = { ...(response.args?.args || {}) };

      if (Array.isArray(change) && Array.isArray(key)) {
        // Handle array inputs by mapping corresponding values
        change.forEach((value, index) => {
          if (index < key.length) {
            updatedArgs[key[index]] = value;
          }
        });
      } else {
        // Handle single value case
        updatedArgs[key as string] = change as string;
      }

      const haveValuesChanged = haveArgsChanged(updatedArgs, initialValues);
      valuesChanged = haveValuesChanged;
    }

    if (!valuesChanged) {
      setHasEdited(false);
      if (acceptAllowed) {
        setSelectedSubmitType("accept");
      } else if (hasAddedResponse) {
        setSelectedSubmitType("response");
      }
    } else {
      setSelectedSubmitType("edit");
      setHasEdited(true);
    }

    setHumanResponse((prev) => {
      if (typeof response.args !== "object" || !response.args) {
        console.error(
          "Mismatched response type",
          !!response.args,
          typeof response.args,
        );
        return prev;
      }

      const newEdit: HumanResponseWithEdits = {
        type: response.type,
        args: {
          action: response.args.action,
          args:
            Array.isArray(change) && Array.isArray(key)
              ? {
                ...response.args.args,
                ...Object.fromEntries(key.map((k, i) => [k, change[i]])),
              }
              : {
                ...response.args.args,
                [key as string]: change as string,
              },
        },
      };
      if (
        prev.find(
          (p) =>
            p.type === response.type &&
            typeof p.args === "object" &&
            p.args?.action === (response.args as ActionRequest).action,
        )
      ) {
        return prev.map((p) => {
          if (
            p.type === response.type &&
            typeof p.args === "object" &&
            p.args?.action === (response.args as ActionRequest).action
          ) {
            if (p.acceptAllowed) {
              return {
                ...newEdit,
                acceptAllowed: true,
                editsMade: valuesChanged,
              };
            }

            return newEdit;
          }
          return p;
        });
      } else {
        throw new Error("No matching response found");
      }
    });
  };

  // 新增：拒绝原因输入处理
  const onRejectChange = (
    change: string,
    response: HumanResponseWithEdits,
  ) => {
    // 设置当前提交类型为“拒绝”
    setSelectedSubmitType("ignore");

    setHumanResponse((prev) => {
      const newResponse: HumanResponseWithEdits = {
        type: response.type,
        args: change,
      };

      if (prev.find((p) => p.type === response.type)) {
        return prev.map((p) => (p.type === response.type ? newResponse : p));
      } else {
        throw new Error("No human response found for reject reason");
      }
    });
  };

  const onResponseChange = (
    change: string,
    response: HumanResponseWithEdits,
  ) => {
    if (!change) {
      setHasAddedResponse(false);
      if (hasEdited) {
        // The user has deleted their response, so we should set the submit type to
        // `edit` if they've edited, or `accept` if it's allowed and they have not edited.
        setSelectedSubmitType("edit");
      } else if (acceptAllowed) {
        setSelectedSubmitType("accept");
      }
    } else {
      setSelectedSubmitType("response");
      setHasAddedResponse(true);
    }

    setHumanResponse((prev) => {
      const newResponse: HumanResponseWithEdits = {
        type: response.type,
        args: change,
      };

      if (prev.find((p) => p.type === response.type)) {
        return prev.map((p) => {
          if (p.type === response.type) {
            if (p.acceptAllowed) {
              return {
                ...newResponse,
                acceptAllowed: true,
                editsMade: !!change,
              };
            }
            return newResponse;
          }
          return p;
        });
      } else {
        throw new Error("No human response found for string response");
      }
    });
  };

  return (
    <CardContainer maxWidth="2xl" spacing="normal">
      {/* 阶段状态显示 # 顶部状态提示 */}
      <PhaseStatusBadge phaseInfo={phaseInfo} />

      {showArgsOutsideActionCards && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <ArgsRenderer args={actionRequestArgs} />
        </div>
      )}

      {selectedSubmitType === "ignore" ? (
        <RejectComponent
          humanResponse={humanResponse}
          streaming={streaming || !phaseInfo.canSubmit}
          onRejectChange={onRejectChange}
          handleSubmit={handleSubmit}
        />
      ) : (
        <EditAndOrAccept
          humanResponse={humanResponse}
          streaming={streaming || !phaseInfo.canSubmit} // 根据状态机禁用输入
          initialValues={initialValues}
          interruptValue={interruptValue}
          actionRequestArgs={actionRequestArgs}
          onEditChange={onEditChange}
          handleSubmit={handleSubmit}
          setSelectedSubmitType={setSelectedSubmitType}
        />
      )}

      {streaming && (
        <div className="flex items-center justify-center gap-2 rounded-lg bg-blue-50 p-3">
          <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
          <p className="text-sm font-medium text-blue-600">执行中...</p>
        </div>
      )}

      {streamFinished && (
        <div className="flex items-center justify-center gap-2 rounded-lg bg-green-50 p-3">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <p className="text-sm font-medium text-green-600">执行完成</p>
        </div>
      )}
    </CardContainer>
  );
}
