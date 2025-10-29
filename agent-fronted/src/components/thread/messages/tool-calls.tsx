import { AIMessage, ToolMessage } from "@langchain/langgraph-sdk";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp } from "lucide-react";
import { QueryResultCard } from "@/components/ui/query-result-card";

function isComplexValue(value: any): boolean {
  return Array.isArray(value) || (typeof value === "object" && value !== null);
}

export function ToolResult({ message }: { message: ToolMessage }) {
  const [isExpanded, setIsExpanded] = useState(false);

  let parsedContent: any;
  let isJsonContent = false;

  try {
    if (typeof message.content === "string") {
      parsedContent = JSON.parse(message.content);
      isJsonContent = isComplexValue(parsedContent);
    }
  } catch {
    // Content is not JSON, use as is
    parsedContent = message.content;
  }

  const contentStr = isJsonContent
    ? JSON.stringify(parsedContent, null, 2)
    : String(message.content);
  const contentLines = contentStr.split("\n");
  const shouldTruncate = contentLines.length > 4 || contentStr.length > 500;
  const displayedContent =
    shouldTruncate && !isExpanded
      ? contentStr.length > 500
        ? contentStr.slice(0, 500) + "..."
        : contentLines.slice(0, 4).join("\n") + "\n..."
      : contentStr;

  return (
    <div className="mx-auto grid max-w-3xl grid-rows-[1fr_auto] gap-2">
      <div className="overflow-hidden rounded-lg border border-gray-200">
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            {message.name ? (
              <h3 className="font-medium text-gray-900">
                Tool Result:{" "}
                <code className="rounded bg-gray-100 px-2 py-1">
                  {message.name}
                </code>
              </h3>
            ) : (
              <h3 className="font-medium text-gray-900">Tool Result</h3>
            )}
            {message.tool_call_id && (
              <code className="ml-2 rounded bg-gray-100 px-2 py-1 text-sm">
                {message.tool_call_id}
              </code>
            )}
          </div>
        </div>
        <motion.div
          className="min-w-full bg-gray-100"
          initial={false}
          animate={{ height: "auto" }}
          transition={{ duration: 0.3 }}
        >
          <div className="p-3">
            <AnimatePresence
              mode="wait"
              initial={false}
            >
              <motion.div
                key={isExpanded ? "expanded" : "collapsed"}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                {isJsonContent ? (
                  <table className="min-w-full divide-y divide-gray-200">
                    <tbody className="divide-y divide-gray-200">
                      {(Array.isArray(parsedContent)
                        ? isExpanded
                          ? parsedContent
                          : parsedContent.slice(0, 5)
                        : Object.entries(parsedContent)
                      ).map((item, argIdx) => {
                        const [key, value] = Array.isArray(parsedContent)
                          ? [argIdx, item]
                          : [item[0], item[1]];
                        return (
                          <tr key={argIdx}>
                            <td className="px-4 py-2 text-sm font-medium whitespace-nowrap text-gray-900">
                              {key}
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-500">
                              {isComplexValue(value) ? (
                                <code className="rounded bg-gray-50 px-2 py-1 font-mono text-sm break-all">
                                  {JSON.stringify(value, null, 2)}
                                </code>
                              ) : (
                                String(value)
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                ) : (
                  <code className="block text-sm">{displayedContent}</code>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
          {((shouldTruncate && !isJsonContent) ||
            (isJsonContent &&
              Array.isArray(parsedContent) &&
              parsedContent.length > 5)) && (
              <motion.button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex w-full cursor-pointer items-center justify-center border-t-[1px] border-gray-200 py-2 text-gray-500 transition-all duration-200 ease-in-out hover:bg-gray-50 hover:text-gray-600"
                initial={{ scale: 1 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isExpanded ? <ChevronUp /> : <ChevronDown />}
              </motion.button>
            )}
        </motion.div>
      </div>
    </div>
  );
}

// Combined Tool Call and Result Card
export function ToolCallWithResult({
  toolCall,
  toolResult,
}: {
  toolCall: NonNullable<AIMessage["tool_calls"]>[number];
  toolResult?: ToolMessage;
}) {
  const args = toolCall.args as Record<string, any>;

  // Format query from tool call args
  // If there's only one argument called 'query', display it directly without showing the parameter name
  const argEntries = Object.entries(args);
  const isSingleQueryArg = argEntries.length === 1 && argEntries[0][0] === 'query';
  const hasNoArgs = argEntries.length === 0;

  const queryContent = hasNoArgs ? (
    // Display empty object for no arguments
    <code className="text-sm text-gray-500">{"{}"}</code>
  ) : isSingleQueryArg ? (
    // Display query value directly without the parameter name
    <div className="text-sm text-gray-900">
      {isComplexValue(argEntries[0][1]) ? (
        <code className="rounded bg-gray-100 px-2 py-1 font-mono text-xs whitespace-pre-wrap break-all">
          {JSON.stringify(argEntries[0][1], null, 2)}
        </code>
      ) : (
        <pre className="whitespace-pre-wrap break-all font-mono">{String(argEntries[0][1])}</pre>
      )}
    </div>
  ) : (
    // Display all arguments in table format
    <table className="min-w-full">
      <tbody className="divide-y divide-gray-200">
        {argEntries.map(([key, value], argIdx) => (
          <tr key={argIdx}>
            <td className="py-1 pr-4 text-sm font-medium text-gray-700">
              {key}
            </td>
            <td className="py-1 text-sm text-gray-900">
              {isComplexValue(value) ? (
                <code className="rounded bg-gray-100 px-2 py-1 font-mono text-xs">
                  {JSON.stringify(value, null, 2)}
                </code>
              ) : (
                <span className="break-all">{String(value)}</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );

  // Format result content
  let resultContent: any = null;
  if (toolResult) {
    let parsedContent: any;
    let isJsonContent = false;

    try {
      if (typeof toolResult.content === "string") {
        parsedContent = JSON.parse(toolResult.content);
        isJsonContent = isComplexValue(parsedContent);
      }
    } catch {
      parsedContent = toolResult.content;
    }

    if (isJsonContent) {
      const items = Array.isArray(parsedContent)
        ? parsedContent
        : Object.entries(parsedContent);

      resultContent = (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <tbody className="divide-y divide-gray-200">
              {items.map((item, argIdx) => {
                const [key, value] = Array.isArray(parsedContent)
                  ? [argIdx, item]
                  : [item[0], item[1]];
                return (
                  <tr key={argIdx}>
                    <td className="px-2 py-2 text-sm font-medium whitespace-nowrap text-gray-900">
                      {key}
                    </td>
                    <td className="px-2 py-2 text-sm text-gray-500">
                      {isComplexValue(value) ? (
                        <code className="rounded bg-gray-50 px-2 py-1 font-mono text-xs break-all">
                          {JSON.stringify(value, null, 2)}
                        </code>
                      ) : (
                        <span className="break-all">{String(value)}</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      );
    } else {
      const contentStr = String(toolResult.content);
      resultContent = (
        <code className="block text-sm whitespace-pre-wrap break-all">
          {contentStr}
        </code>
      );
    }
  }

  const queryTitle = toolCall.name;

  return (
    <QueryResultCard
      query={queryContent}
      result={resultContent || <span className="text-sm text-muted-foreground">No result available</span>}
      queryTitle={queryTitle}
      resultTitle="Tool Result"
      defaultExpanded={false}
      className="w-full"
    />
  );
}
