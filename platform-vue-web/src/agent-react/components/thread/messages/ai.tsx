import { parsePartialJson } from "@langchain/core/output_parsers";
import { useStreamContext } from "@/providers/Stream";
import { AIMessage, Checkpoint, Message, ToolMessage } from "@langchain/langgraph-sdk";
import { getContentString } from "../utils";
import { BranchSwitcher, CommandBar } from "./shared";
import { MarkdownText } from "../markdown-text";
import { LoadExternalComponent } from "@langchain/langgraph-sdk/react-ui";
import { cn } from "@/lib/utils";
import { ToolResult, ToolCallWithResult } from "./tool-calls";
import { MessageContentComplex } from "@langchain/core/messages";
import { Fragment } from "react/jsx-runtime";
import { isAgentInboxInterruptSchema } from "@/lib/agent-inbox-interrupt";
import { ThreadView } from "../agent-inbox";
import { useQueryState, parseAsBoolean } from "nuqs";
import { GenericInterruptView } from "./generic-interrupt";
import { useArtifact } from "../artifact";

function CustomComponent({
  message,
  thread,
}: {
  message: Message;
  thread: ReturnType<typeof useStreamContext>;
}) {
  const artifact = useArtifact();
  const { values } = useStreamContext();
  const customComponents = values.ui?.filter(
    (ui) => ui.metadata?.message_id === message.id,
  );

  if (!customComponents?.length) return null;
  return (
    <Fragment key={message.id}>
      {customComponents.map((customComponent) => (
        <LoadExternalComponent
          key={customComponent.id}
          stream={thread}
          message={customComponent}
          meta={{ ui: customComponent, artifact }}
        />
      ))}
    </Fragment>
  );
}

function parseAnthropicStreamedToolCalls(
  content: MessageContentComplex[],
): AIMessage["tool_calls"] {
  const toolCallContents = content.filter((c) => c.type === "tool_use" && c.id);

  return toolCallContents.map((tc) => {
    const toolCall = tc as Record<string, any>;
    let json: Record<string, any> = {};
    if (toolCall?.input) {
      try {
        json = parsePartialJson(toolCall.input) ?? {};
      } catch {
        // Pass
      }
    }
    return {
      name: toolCall.name ?? "",
      id: toolCall.id ?? "",
      args: json,
      type: "tool_call",
    };
  });
}

interface InterruptProps {
  interruptValue?: unknown;
  isLastMessage: boolean;
  hasNoAIOrToolMessages: boolean;
}

function Interrupt({
  interruptValue,
  isLastMessage,
  hasNoAIOrToolMessages,
}: InterruptProps) {
  return (
    <>
      {isAgentInboxInterruptSchema(interruptValue) &&
        (isLastMessage || hasNoAIOrToolMessages) && (
          <ThreadView interrupt={interruptValue} />
        )}
      {interruptValue &&
        !isAgentInboxInterruptSchema(interruptValue) &&
        (isLastMessage || hasNoAIOrToolMessages) ? (
        <GenericInterruptView interrupt={interruptValue} />
      ) : null}
    </>
  );
}

export function AssistantMessage({
  message,
  isLoading,
  handleRegenerate,
}: {
  message: Message | undefined;
  isLoading: boolean;
  handleRegenerate: (parentCheckpoint: Checkpoint | null | undefined) => void;
}) {
  const content = message?.content ?? [];
  const contentString = getContentString(content);
  const [hideToolCalls] = useQueryState(
    "hideToolCalls",
    parseAsBoolean.withDefault(false),
  );

  const thread = useStreamContext();
  const isLastMessage =
    thread.messages[thread.messages.length - 1].id === message?.id;
  const hasNoAIOrToolMessages = !thread.messages.find(
    (m) => m.type === "ai" || m.type === "tool",
  );
  const meta = message ? thread.getMessagesMetadata(message) : undefined;
  const threadInterrupt = thread.interrupt;

  const parentCheckpoint = meta?.firstSeenState?.parent_checkpoint;
  const anthropicStreamedToolCalls = Array.isArray(content)
    ? parseAnthropicStreamedToolCalls(content)
    : undefined;

  const hasToolCalls =
    message &&
    "tool_calls" in message &&
    message.tool_calls &&
    message.tool_calls.length > 0;
  const toolCallsHaveContents =
    hasToolCalls &&
    message.tool_calls?.some(
      (tc) => tc.args && Object.keys(tc.args).length > 0,
    );
  const hasAnthropicToolCalls = !!anthropicStreamedToolCalls?.length;
  const isToolResult = message?.type === "tool";

  // 合并并去重工具调用（基于ID）
  const allToolCalls = (() => {
    const calls: NonNullable<AIMessage["tool_calls"]> = [];
    const seenIds = new Set<string>();

    // 优先使用 message.tool_calls
    if (hasToolCalls && message.tool_calls) {
      for (const tc of message.tool_calls) {
        if (tc.id && tc.name && tc.args) {
          calls.push(tc);
          seenIds.add(tc.id);
        }
      }
    }

    // 添加 Anthropic 工具调用（如果不重复）
    if (hasAnthropicToolCalls && anthropicStreamedToolCalls) {
      for (const tc of anthropicStreamedToolCalls) {
        if (tc.id && tc.name && tc.args && !seenIds.has(tc.id)) {
          calls.push(tc);
          seenIds.add(tc.id);
        }
      }
    }

    return calls;
  })();

  // Find tool results for this AI message's tool calls
  const toolResults: Record<string, ToolMessage> = {};
  if (allToolCalls.length > 0 && message) {
    const currentMessageIndex = thread.messages.findIndex((m) => m.id === message.id);
    // Look at the next few messages for tool results
    for (let i = currentMessageIndex + 1; i < thread.messages.length && i < currentMessageIndex + 10; i++) {
      const msg = thread.messages[i];
      if (msg.type === "tool" && "tool_call_id" in msg && msg.tool_call_id) {
        toolResults[msg.tool_call_id] = msg as ToolMessage;
      }
      // Stop if we hit another AI message
      if (msg.type === "ai") break;
    }
  }

  // 统计每个工具调用的尝试次数（仅统计当前回合，从最近的人类消息开始）
  const toolCallAttempts = new Map<string, number>();
  if (message) {
    const currentMessageIndex = thread.messages.findIndex((m) => m.id === message.id);

    // 找到当前消息之前最近的人类消息索引
    let lastHumanMessageIndex = -1;
    for (let i = currentMessageIndex - 1; i >= 0; i--) {
      if (thread.messages[i].type === "human") {
        lastHumanMessageIndex = i;
        break;
      }
    }

    // 只统计从最近的人类消息到当前消息之间的工具调用（当前回合内）
    const startIndex = lastHumanMessageIndex >= 0 ? lastHumanMessageIndex : 0;
    for (let i = startIndex; i <= currentMessageIndex; i++) {
      const msg = thread.messages[i];
      if (msg.type === "ai" && "tool_calls" in msg && msg.tool_calls) {
        for (const tc of msg.tool_calls) {
          if (tc.name) {
            const currentCount = toolCallAttempts.get(tc.name) || 0;
            toolCallAttempts.set(tc.name, currentCount + 1);
          }
        }
      }
    }
  }

  // 检查后续消息中是否有相同工具名的调用（仅当前回合，到下一个人类消息为止）
  const toolNamesInLaterMessages = new Set<string>();
  if (message) {
    const currentMessageIndex = thread.messages.findIndex((m) => m.id === message.id);

    // 找到当前消息之后下一个人类消息的索引
    let nextHumanMessageIndex = thread.messages.length;
    for (let i = currentMessageIndex + 1; i < thread.messages.length; i++) {
      if (thread.messages[i].type === "human") {
        nextHumanMessageIndex = i;
        break;
      }
    }

    // 只检查当前回合内的后续消息（从当前消息到下一个人类消息之间）
    for (let i = currentMessageIndex + 1; i < nextHumanMessageIndex; i++) {
      const laterMsg = thread.messages[i];
      if (laterMsg.type === "ai" && "tool_calls" in laterMsg && laterMsg.tool_calls) {
        for (const tc of laterMsg.tool_calls) {
          if (tc.name) {
            toolNamesInLaterMessages.add(tc.name);
          }
        }
      }
    }
  }

  // 过滤：如果后续有相同工具名，就隐藏当前的
  const filteredToolCalls = allToolCalls.filter((tc) => {
    if (!tc.name) return true;

    // 如果后续消息中有相同工具名，隐藏当前的
    return !toolNamesInLaterMessages.has(tc.name);
  });

  const hasAnyToolCalls = filteredToolCalls.length > 0;

  // Hide tool results if they are already shown in the merged card or if hideToolCalls is true
  if (isToolResult) {
    if (hideToolCalls) {
      return null;
    }
    // Check if this tool result has already been displayed in a merged card
    const toolCallId = "tool_call_id" in message ? message.tool_call_id : undefined;
    if (toolCallId) {
      // Find if there's an AI message before this one that has the corresponding tool call
      const currentIndex = thread.messages.findIndex((m) => m.id === message.id);
      for (let i = currentIndex - 1; i >= 0 && i >= currentIndex - 10; i--) {
        const prevMsg = thread.messages[i];
        if (prevMsg.type === "ai" && "tool_calls" in prevMsg && prevMsg.tool_calls) {
          const hasMatchingToolCall = prevMsg.tool_calls.some((tc) => tc.id === toolCallId);
          if (hasMatchingToolCall) {
            // This tool result is already displayed in the merged card, don't show it again
            return null;
          }
        }
      }
    }
  }

  return (
    <div className="group w-full flex items-start gap-2">
      <div className="flex flex-col gap-2 w-full">
        {isToolResult ? (
          <>
            <ToolResult message={message} />
            <Interrupt
              interruptValue={threadInterrupt?.value}
              isLastMessage={isLastMessage}
              hasNoAIOrToolMessages={hasNoAIOrToolMessages}
            />
          </>
        ) : (
          <>
            {contentString.length > 0 && (
              <div className="w-full flex justify-start">
                <div className="max-w-2xl py-1 mb-4">
                  <MarkdownText>{contentString}</MarkdownText>
                </div>
              </div>
            )}

            {!hideToolCalls && hasAnyToolCalls && (
              <div className="flex flex-col gap-4 w-full">
                {filteredToolCalls.map((tc, idx) => {
                  const attemptNumber = tc.name ? toolCallAttempts.get(tc.name) : undefined;
                  return (
                    <ToolCallWithResult
                      key={tc.id || idx}
                      toolCall={tc}
                      toolResult={tc.id ? toolResults[tc.id] : undefined}
                      attemptNumber={attemptNumber}
                    />
                  );
                })}
              </div>
            )}

            {message && (
              <CustomComponent
                message={message}
                thread={thread}
              />
            )}
            <Interrupt
              interruptValue={threadInterrupt?.value}
              isLastMessage={isLastMessage}
              hasNoAIOrToolMessages={hasNoAIOrToolMessages}
            />
            <div
              className={cn(
                "mr-auto flex items-center gap-2 transition-opacity",
                "opacity-0 group-focus-within:opacity-100 group-hover:opacity-100",
              )}
            >
              <BranchSwitcher
                branch={meta?.branch}
                branchOptions={meta?.branchOptions}
                onSelect={(branch) => thread.setBranch(branch)}
                isLoading={isLoading}
              />
              <CommandBar
                content={contentString}
                isLoading={isLoading}
                isAiMessage={true}
                handleRegenerate={() => handleRegenerate(parentCheckpoint)}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export function AssistantMessageLoading() {
  return (
    <div className="mr-auto flex items-start gap-2">
      <div className="bg-muted flex h-8 items-center gap-1 rounded-2xl px-4 py-2">
        <div className="bg-foreground/50 h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_infinite] rounded-full"></div>
        <div className="bg-foreground/50 h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_0.5s_infinite] rounded-full"></div>
        <div className="bg-foreground/50 h-1.5 w-1.5 animate-[pulse_1.5s_ease-in-out_1s_infinite] rounded-full"></div>
      </div>
    </div>
  );
}
