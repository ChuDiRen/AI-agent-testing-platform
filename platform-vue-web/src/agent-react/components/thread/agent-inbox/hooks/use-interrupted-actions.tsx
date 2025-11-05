import { HumanResponseWithEdits, SubmitType, InterruptState, InterruptPhaseInfo } from "../types";
import {
  KeyboardEvent,
  Dispatch,
  SetStateAction,
  MutableRefObject,
  useState,
  useRef,
  useEffect,
  useCallback,
} from "react";
import { createDefaultHumanResponse } from "../utils";
import { toast } from "sonner";
import { HumanInterrupt, HumanResponse } from "@langchain/langgraph/prebuilt";
import { END } from "@langchain/langgraph/web";
import { useStreamContext } from "@/providers/Stream";

interface UseInterruptedActionsInput {
  interrupt: HumanInterrupt;
}

// 状态机辅助函数 # 获取当前阶段信息
function getPhaseInfo(state: InterruptState): InterruptPhaseInfo {
  switch (state) {
    case "idle":
      return {
        state,
        message: "",
        canSubmit: false,
        canCancel: false,
        showContinue: false,
      };
    case "interrupted":
      return {
        state,
        message: "等待您的响应...",
        canSubmit: true,
        canCancel: true,
        showContinue: false,
      };
    case "responding":
      return {
        state,
        message: "正在输入响应...",
        canSubmit: true,
        canCancel: true,
        showContinue: false,
      };
    case "submitting":
      return {
        state,
        message: "正在提交响应...",
        canSubmit: false,
        canCancel: false,
        showContinue: false,
      };
    case "processing":
      return {
        state,
        message: "后端正在处理，请稍候...",
        canSubmit: false,
        canCancel: true,
        showContinue: false,
      };
    case "resumed":
      return {
        state,
        message: "执行已恢复",
        canSubmit: false,
        canCancel: false,
        showContinue: true,
      };
    case "completed":
      return {
        state,
        message: "处理完成",
        canSubmit: false,
        canCancel: false,
        showContinue: false,
      };
    case "error":
      return {
        state,
        message: "发生错误，请重试",
        canSubmit: true,
        canCancel: true,
        showContinue: false,
      };
    default:
      return {
        state: "idle",
        message: "",
        canSubmit: false,
        canCancel: false,
        showContinue: false,
      };
  }
}

interface UseInterruptedActionsValue {
  // Actions
  handleSubmit: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | KeyboardEvent,
  ) => Promise<void>;
  handleIgnore: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => Promise<void>;
  handleResolve: (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => Promise<void>;
  handleContinue: () => void; // 新增：继续处理

  // State values
  streaming: boolean;
  streamFinished: boolean;
  loading: boolean;
  supportsMultipleMethods: boolean;
  hasEdited: boolean;
  hasAddedResponse: boolean;
  acceptAllowed: boolean;
  humanResponse: HumanResponseWithEdits[];

  // 新增：状态机相关 # 状态机状态
  interruptState: InterruptState;
  phaseInfo: InterruptPhaseInfo;

  // State setters
  setSelectedSubmitType: Dispatch<SetStateAction<SubmitType | undefined>>;
  setHumanResponse: Dispatch<SetStateAction<HumanResponseWithEdits[]>>;
  setHasAddedResponse: Dispatch<SetStateAction<boolean>>;
  setHasEdited: Dispatch<SetStateAction<boolean>>;

  // Refs
  initialHumanInterruptEditValue: MutableRefObject<Record<string, string>>;
}

export default function useInterruptedActions({
  interrupt,
}: UseInterruptedActionsInput): UseInterruptedActionsValue {
  const thread = useStreamContext();
  const [humanResponse, setHumanResponse] = useState<HumanResponseWithEdits[]>(
    [],
  );
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [streamFinished, setStreamFinished] = useState(false);
  const initialHumanInterruptEditValue = useRef<Record<string, string>>({});
  const [selectedSubmitType, setSelectedSubmitType] = useState<SubmitType>();
  // Whether or not the user has edited any fields which allow editing.
  const [hasEdited, setHasEdited] = useState(false);
  // Whether or not the user has added a response.
  const [hasAddedResponse, setHasAddedResponse] = useState(false);
  const [acceptAllowed, setAcceptAllowed] = useState(false);

  // 新增：状态机状态 # 状态机管理
  const [interruptState, setInterruptState] = useState<InterruptState>("idle");
  const phaseInfo = getPhaseInfo(interruptState);

  // 初始化中断响应 # 当interrupt变化时重置状态
  useEffect(() => {
    try {
      const { responses, defaultSubmitType, hasAccept } =
        createDefaultHumanResponse(interrupt, initialHumanInterruptEditValue);
      setSelectedSubmitType(defaultSubmitType);
      setHumanResponse(responses);
      setAcceptAllowed(hasAccept);

      // 重置状态机为interrupted # 新的中断到来
      setInterruptState("interrupted");
      setStreaming(false);
      setStreamFinished(false);
      setLoading(false);
    } catch (e) {
      console.error("Error formatting and setting human response state", e);
      setInterruptState("error");
    }
  }, [interrupt]);

  const resumeRun = (response: HumanResponse[]): boolean => {
    try {
      thread.submit(
        {},
        {
          command: {
            resume: response,
          },
        },
      );
      return true;
    } catch (e: any) {
      console.error("Error sending human response", e);
      return false;
    }
  };

  const handleSubmit = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent> | KeyboardEvent,
  ) => {
    e.preventDefault();
    if (!humanResponse) {
      toast.error("Error", {
        description: "Please enter a response.",
        duration: 5000,
        richColors: true,
        closeButton: true,
      });
      return;
    }

    // 状态转换：responding -> submitting # 开始提交
    setInterruptState("submitting");
    let errorOccurred = false;
    initialHumanInterruptEditValue.current = {};

    if (
      humanResponse.some((r) => ["response", "edit", "accept"].includes(r.type))
    ) {
      setStreamFinished(false);

      try {
        const humanResponseInput: HumanResponse[] = humanResponse.flatMap(
          (r) => {
            if (r.type === "edit") {
              if (r.acceptAllowed && !r.editsMade) {
                return {
                  type: "accept",
                  args: r.args,
                };
              } else {
                return {
                  type: "edit",
                  args: r.args,
                };
              }
            }

            if (r.type === "response" && !r.args) {
              // If response was allowed but no response was given, do not include in the response
              return [];
            }
            return {
              type: r.type,
              args: r.args,
            };
          },
        );

        const input = humanResponseInput.find(
          (r) => r.type === selectedSubmitType,
        );
        if (!input) {
          toast.error("Error", {
            description: "No response found.",
            richColors: true,
            closeButton: true,
            duration: 5000,
          });
          setInterruptState("error"); // 状态转换：submitting -> error
          return;
        }

        setLoading(true);
        setStreaming(true);

        // 状态转换：submitting -> processing # 后端开始处理
        setInterruptState("processing");

        const resumedSuccessfully = resumeRun([input]);
        if (!resumedSuccessfully) {
          setInterruptState("error"); // 状态转换：processing -> error
          setLoading(false);
          setStreaming(false);
          return;
        }

        toast("Success", {
          description: "Response submitted successfully.",
          duration: 5000,
        });

        // 状态转换：processing -> resumed # 执行已恢复
        setInterruptState("resumed");

        if (!errorOccurred) {
          setStreamFinished(true);
        }
      } catch (e: any) {
        console.error("Error sending human response", e);

        if ("message" in e && e.message.includes("Invalid assistant ID")) {
          toast("Error: Invalid assistant ID", {
            description:
              "The provided assistant ID was not found in this graph. Please update the assistant ID in the settings and try again.",
            richColors: true,
            closeButton: true,
            duration: 5000,
          });
        } else {
          toast.error("Error", {
            description: "Failed to submit response.",
            richColors: true,
            closeButton: true,
            duration: 5000,
          });
        }

        errorOccurred = true;
        setInterruptState("error"); // 状态转换：-> error
        setStreaming(false);
        setStreamFinished(false);
      }

      if (!errorOccurred) {
        setStreaming(false);
        // 不立即设置为false，等待后续处理完成
        // setStreamFinished(false);
      }
    } else {
      setLoading(true);
      setInterruptState("processing"); // 状态转换：submitting -> processing

      resumeRun(humanResponse);

      toast("Success", {
        description: "Response submitted successfully.",
        duration: 5000,
      });

      setInterruptState("resumed"); // 状态转换：processing -> resumed
    }

    setLoading(false);
  };

  const handleIgnore = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();

    const ignoreResponse = humanResponse.find((r) => r.type === "ignore");
    if (!ignoreResponse) {
      toast.error("Error", {
        description: "The selected thread does not support ignoring.",
        duration: 5000,
      });
      return;
    }

    setLoading(true);
    setInterruptState("processing"); // 状态转换：interrupted -> processing
    initialHumanInterruptEditValue.current = {};

    resumeRun([ignoreResponse]);

    setLoading(false);
    setInterruptState("completed"); // 状态转换：processing -> completed
    toast("Successfully ignored thread", {
      duration: 5000,
    });
  };

  const handleResolve = async (
    e: React.MouseEvent<HTMLButtonElement, MouseEvent>,
  ) => {
    e.preventDefault();

    setLoading(true);
    setInterruptState("processing"); // 状态转换：interrupted -> processing
    initialHumanInterruptEditValue.current = {};

    try {
      thread.submit(
        {},
        {
          command: {
            goto: END,
          },
        },
      );

      setInterruptState("completed"); // 状态转换：processing -> completed
      toast("Success", {
        description: "Marked thread as resolved.",
        duration: 3000,
      });
    } catch (e) {
      console.error("Error marking thread as resolved", e);
      setInterruptState("error"); // 状态转换：processing -> error
      toast.error("Error", {
        description: "Failed to mark thread as resolved.",
        richColors: true,
        closeButton: true,
        duration: 3000,
      });
    }

    setLoading(false);
  };

  // 新增：继续处理函数 # 用户点击继续按钮
  const handleContinue = useCallback(() => {
    // 状态转换：resumed -> idle，准备接收新的中断
    setInterruptState("idle");
    setStreamFinished(false);
    setStreaming(false);
    setLoading(false);

    toast("Ready for next interrupt", {
      description: "System is ready to handle new interrupts.",
      duration: 3000,
    });
  }, []);

  const supportsMultipleMethods =
    humanResponse.filter(
      (r) => r.type === "edit" || r.type === "accept" || r.type === "response",
    ).length > 1;

  return {
    handleSubmit,
    handleIgnore,
    handleResolve,
    handleContinue, // 新增：继续处理函数
    humanResponse,
    streaming,
    streamFinished,
    loading,
    supportsMultipleMethods,
    hasEdited,
    hasAddedResponse,
    acceptAllowed,
    interruptState, // 新增：状态机状态
    phaseInfo, // 新增：阶段信息
    setSelectedSubmitType,
    setHumanResponse,
    setHasAddedResponse,
    setHasEdited,
    initialHumanInterruptEditValue,
  };
}
