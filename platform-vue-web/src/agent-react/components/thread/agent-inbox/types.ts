import { BaseMessage } from "@langchain/core/messages";
import { Thread, ThreadStatus } from "@langchain/langgraph-sdk";
import { HumanInterrupt, HumanResponse } from "@langchain/langgraph/prebuilt";

export type HumanResponseWithEdits = HumanResponse &
  (
    | { acceptAllowed?: false; editsMade?: never }
    | { acceptAllowed?: true; editsMade?: boolean }
  );

export type Email = {
  id: string;
  thread_id: string;
  from_email: string;
  to_email: string;
  subject: string;
  page_content: string;
  send_time: string | undefined;
  read?: boolean;
  status?: "in-queue" | "processing" | "hitl" | "done";
};

export interface ThreadValues {
  email: Email;
  messages: BaseMessage[];
  triage: {
    logic: string;
    response: string;
  };
}

export type ThreadData<
  ThreadValues extends Record<string, any> = Record<string, any>,
> = {
  thread: Thread<ThreadValues>;
} & (
    | {
      status: "interrupted";
      interrupts: HumanInterrupt[] | undefined;
    }
    | {
      status: "idle" | "busy" | "error";
      interrupts?: never;
    }
  );

export type ThreadStatusWithAll = ThreadStatus | "all";

export type SubmitType = "accept" | "response" | "edit" | "ignore";

// 中断处理状态机 # 状态机定义
export type InterruptState =
  | "idle"          // 空闲状态，无中断
  | "interrupted"   // 已中断，等待用户响应
  | "responding"    // 用户正在输入响应
  | "submitting"    // 正在提交响应到后端
  | "processing"    // 后端正在处理
  | "resumed"       // 已恢复执行
  | "completed"     // 处理完成
  | "error";        // 发生错误

// 中断处理阶段信息 # UI反馈数据
export interface InterruptPhaseInfo {
  state: InterruptState;
  message: string;
  canSubmit: boolean;
  canCancel: boolean;
  showContinue: boolean;
}

export interface AgentInbox {
  /**
   * A unique identifier for the inbox.
   */
  id: string;
  /**
   * The ID of the graph.
   */
  graphId: string;
  /**
   * The URL of the deployment. Either a localhost URL, or a deployment URL.
   */
  deploymentUrl: string;
  /**
   * Optional name for the inbox, used in the UI to label the inbox.
   */
  name?: string;
  /**
   * Whether or not the inbox is selected.
   */
  selected: boolean;
}
