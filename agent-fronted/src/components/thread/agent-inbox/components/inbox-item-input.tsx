import { HumanResponseWithEdits, SubmitType, InterruptPhaseInfo } from "../types";
import { Textarea } from "@/components/ui/textarea";
import React from "react";
import { haveArgsChanged, prettifyText } from "../utils";
import { Button } from "@/components/ui/button";
import { Undo2, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { MarkdownText } from "../../markdown-text";
import { ActionRequest, HumanInterrupt } from "@langchain/langgraph/prebuilt";
import { toast } from "sonner";
import { Separator } from "@/components/ui/separator";
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
      <span>Reset</span>
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

        return (
          <div
            key={`args-${k}`}
            className="flex flex-col items-start gap-2"
          >
            <p className="text-sm font-medium text-gray-700">
              {prettifyText(k)}:
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
  ) => Promise<void>;
}

function ResponseComponent({
  humanResponse,
  streaming,
  showArgsInResponse,
  interruptValue,
  onResponseChange,
  handleSubmit,
}: {
  humanResponse: HumanResponseWithEdits[];
  streaming: boolean;
  showArgsInResponse: boolean;
  interruptValue: HumanInterrupt;
  onResponseChange: (change: string, response: HumanResponseWithEdits) => void;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
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
          <p className="text-base font-semibold text-black">
            Respond to assistant
          </p>
          <ResetButton
            handleReset={() => {
              onResponseChange("", res);
            }}
          />
        </div>

        {showArgsInResponse && (
          <ArgsRenderer args={interruptValue.action_request.args} />
        )}

        <div className="flex w-full flex-col items-start gap-2">
          <p className="min-w-fit text-sm font-medium">Response</p>
          <Textarea
            disabled={streaming}
            value={res.args}
            onChange={(e) => onResponseChange(e.target.value, res)}
            onKeyDown={handleKeyDown}
            rows={4}
            placeholder="Your response here..."
          />
        </div>

        <div className="flex w-full items-center justify-end gap-2">
          <Button
            variant="brand"
            disabled={streaming}
            onClick={handleSubmit}
          >
            Send Response
          </Button>
        </div>
      </div>
    </UnifiedCard>
  );
}
const Response = React.memo(ResponseComponent);

function AcceptComponent({
  streaming,
  actionRequestArgs,
  handleSubmit,
}: {
  streaming: boolean;
  actionRequestArgs: Record<string, any>;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
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
          onClick={handleSubmit}
          className="w-full"
        >
          Accept
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
}: {
  humanResponse: HumanResponseWithEdits[];
  streaming: boolean;
  initialValues: Record<string, string>;
  interruptValue: HumanInterrupt;
  onEditChange: (
    text: string | string[],
    response: HumanResponseWithEdits,
    key: string | string[],
  ) => void;
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | React.KeyboardEvent,
  ) => Promise<void>;
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
          actionRequestArgs={interruptValue.action_request.args}
          streaming={streaming}
          handleSubmit={handleSubmit}
        />
      );
    }
    return null;
  }
  const header = editResponse.acceptAllowed ? "Edit/Accept" : "Edit";
  let buttonText = "Submit";
  if (editResponse.acceptAllowed && !editResponse.editsMade) {
    buttonText = "Accept";
  }

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
          <Button
            variant="brand"
            disabled={streaming}
            onClick={handleSubmit}
          >
            {buttonText}
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
  setHumanResponse,
  setSelectedSubmitType,
  setHasEdited,
  setHasAddedResponse,
  handleSubmit,
}: InboxItemInputProps) {
  const isEditAllowed = interruptValue.config.allow_edit;
  const isResponseAllowed = interruptValue.config.allow_respond;
  const hasArgs = Object.entries(interruptValue.action_request.args).length > 0;
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
          <ArgsRenderer args={interruptValue.action_request.args} />
        </div>
      )}

      <EditAndOrAccept
        humanResponse={humanResponse}
        streaming={streaming || !phaseInfo.canSubmit} // 根据状态机禁用输入
        initialValues={initialValues}
        interruptValue={interruptValue}
        onEditChange={onEditChange}
        handleSubmit={handleSubmit}
      />

      {supportsMultipleMethods && (
        <div className="flex items-center gap-3">
          <Separator className="flex-1" />
          <p className="text-sm font-medium text-gray-500">Or</p>
          <Separator className="flex-1" />
        </div>
      )}

      <Response
        humanResponse={humanResponse}
        streaming={streaming || !phaseInfo.canSubmit} // 根据状态机禁用输入
        showArgsInResponse={showArgsInResponse}
        interruptValue={interruptValue}
        onResponseChange={onResponseChange}
        handleSubmit={handleSubmit}
      />

      {streaming && (
        <div className="flex items-center justify-center gap-2 rounded-lg bg-blue-50 p-3">
          <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
          <p className="text-sm font-medium text-blue-600">Running...</p>
        </div>
      )}

      {streamFinished && (
        <div className="flex items-center justify-center gap-2 rounded-lg bg-green-50 p-3">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <p className="text-sm font-medium text-green-600">
            Successfully finished Graph invocation.
          </p>
        </div>
      )}
    </CardContainer>
  );
}
