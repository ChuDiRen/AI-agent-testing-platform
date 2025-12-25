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
import { useState } from "react";
import { ChevronDown, ChevronUp, Wrench } from "lucide-react";

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

interface ToolCallsSummaryProps {
  toolCalls: NonNullable<AIMessage["tool_calls"]>;
  toolResults: Record<string, ToolMessage>;
  toolCallAttempts: Map<string, number>;
}

function ToolCallsSummary({
  toolCalls,
  toolResults,
  toolCallAttempts,
}: ToolCallsSummaryProps) {
  const [isExpanded, setIsExpanded] = useState(false); // 默认折叠，用户可点击展开

  if (toolCalls.length === 0) return null;

  // 统计工具类型
  const toolStats = toolCalls.reduce((acc, tc) => {
    if (tc.name) {
      acc[tc.name] = (acc[tc.name] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  const toolCount = toolCalls.length;
  const uniqueToolCount = Object.keys(toolStats).length;

  return (
    <div className="w-full mb-4">
      {/* 执行摘要卡片 */}
      <div
        className={cn(
          "rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden"
        )}
      >
        <div
          className={cn(
            "flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-gray-50 transition-colors",
            isExpanded && "border-b border-gray-200 bg-gray-50"
          )}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-200">
              <Wrench className="h-3 w-3 text-gray-600" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-medium text-gray-700">
                执行了 {toolCount} 个工具调用
              </span>
              {!isExpanded && (
                <span className="text-[10px] text-gray-500 truncate max-w-md">
                  {Object.keys(toolStats).slice(0, 3).join(", ")}{Object.keys(toolStats).length > 3 ? "..." : ""}
                </span>
              )}
            </div>
          </div>
          <button
            className={cn(
              "p-1 rounded transition-transform duration-300",
              isExpanded && "rotate-180"
            )}
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            <ChevronDown className="h-3 w-3 text-gray-500" />
          </button>
        </div>

        {/* 工具调用详情 */}
        {isExpanded && (
          <div className="px-4 py-3 space-y-4 bg-white">
            {toolCalls.map((tc, idx) => {
              const attemptNumber = tc.name ? toolCallAttempts.get(tc.name) : undefined;
              const args = tc.args as Record<string, any>;
              const toolResult = tc.id ? toolResults[tc.id] : undefined;

              // 解析结果
              let resultData: any = undefined;
              if (toolResult) {
                try {
                  if (typeof toolResult.content === "string") {
                    resultData = JSON.parse(toolResult.content);
                  } else {
                    resultData = toolResult.content;
                  }
                } catch {
                  resultData = toolResult.content;
                }
              }

              // 检测是否是图片 URL
              const isImageUrl = (str: string): boolean => {
                if (typeof str !== 'string') return false;
                const imageUrlPattern = /^https?:\/\/.+\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i;
                const imagePathPattern = /^https?:\/\/.+\/(img|image|images|afts\/img|picture|pic)\//i;
                const cdnImagePattern = /^https?:\/\/(mdn\.alipayobjects\.com|.*cdn.*)\/.*(\/img\/|\/image\/|\/original)/i;
                return imageUrlPattern.test(str) || imagePathPattern.test(str) || cdnImagePattern.test(str);
              };

              // 获取图片 URL
              const getImageUrl = (data: any): string | null => {
                if (typeof data === 'string' && isImageUrl(data)) return data;
                if (typeof data === 'object' && data !== null) {
                  const possibleKeys = ['image', 'imageUrl', 'image_url', 'url', 'src', 'chart', 'chartUrl', 'chart_url'];
                  for (const key of possibleKeys) {
                    if (data[key] && typeof data[key] === 'string' && isImageUrl(data[key])) {
                      return data[key];
                    }
                  }
                }
                return null;
              };

              // 清理 markdown 代码块标记
              const cleanResult = (data: any): string => {
                let text = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                // 移除 markdown 代码块标记 ```sql 或 ``` 
                text = text.replace(/^```\w*\n?/gm, '').replace(/\n?```$/gm, '');
                return text.trim();
              };

              const imageUrl = getImageUrl(resultData);

              return (
                <div key={tc.id || idx} className="space-y-3">
                  {/* 工具名称 */}
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-800">{tc.name}</span>
                    {attemptNumber && attemptNumber > 1 && (
                      <span className="text-xs text-gray-500">(尝试 {attemptNumber})</span>
                    )}
                  </div>

                  {/* 参数 */}
                  <div>
                    <div className="text-xs font-semibold text-gray-600 uppercase mb-1">参数</div>
                    <pre className="text-xs bg-gray-50 rounded border border-gray-200 p-2 overflow-x-auto">
                      {JSON.stringify(args || {}, null, 2)}
                    </pre>
                  </div>

                  {/* 结果 */}
                  {resultData && (
                    <div>
                      <div className="text-xs font-semibold text-gray-600 uppercase mb-1">结果</div>
                      {imageUrl ? (
                        <div className="bg-gray-50 rounded border border-gray-200 p-3 space-y-2">
                          <img
                            src={imageUrl}
                            alt="生成的图表"
                            className="max-w-full h-auto"
                            crossOrigin="anonymous"
                            onError={(e) => {
                              // 图片加载失败时隐藏图片，显示链接
                              e.currentTarget.style.display = 'none';
                              const link = e.currentTarget.nextElementSibling;
                              if (link) link.classList.remove('hidden');
                            }}
                          />
                          <a
                            href={imageUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hidden text-sm text-blue-600 hover:underline break-all"
                          >
                            点击查看图表：{imageUrl}
                          </a>
                        </div>
                      ) : (
                        <pre className="text-xs bg-gray-50 rounded border border-gray-200 p-2 overflow-x-auto max-h-60 overflow-y-auto">
                          {cleanResult(resultData)}
                        </pre>
                      )}
                    </div>
                  )}

                  {/* 分隔线 */}
                  {idx < toolCalls.length - 1 && <div className="border-t border-gray-100" />}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
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

  // 检查是否应该显示工具调用摘要（只要有工具调用就显示）
  const shouldShowToolSummary = (() => {
    if (!message || message.type !== "ai") return false;
    // 只要是 AI 消息就显示（即使没有文本内容）
    return true;
  })();

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
        if (tc.id && tc.name) {
          calls.push(tc);
          seenIds.add(tc.id);
        }
      }
    }

    // 添加 Anthropic 工具调用（如果不重复）
    if (hasAnthropicToolCalls && anthropicStreamedToolCalls) {
      for (const tc of anthropicStreamedToolCalls) {
        if (tc.id && tc.name && !seenIds.has(tc.id)) {
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

  // 不再过滤工具调用，显示所有工具调用
  const filteredToolCalls = allToolCalls;

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
              <div className="w-full mb-4">
                <div className="prose prose-slate max-w-none">
                  <MarkdownText>{contentString}</MarkdownText>
                </div>
              </div>
            )}

            {message && (
              <CustomComponent
                message={message}
                thread={thread}
              />
            )}

            {!hideToolCalls && hasAnyToolCalls && shouldShowToolSummary && (
              <ToolCallsSummary
                toolCalls={filteredToolCalls}
                toolResults={toolResults}
                toolCallAttempts={toolCallAttempts}
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
