import * as React from "react";
import { ChevronDown, Sparkles, Copy, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface QueryResultCardProps {
    query: React.ReactNode;
    result: React.ReactNode;
    queryTitle?: React.ReactNode;
    resultTitle?: React.ReactNode;
    defaultExpanded?: boolean;
    timestamp?: string;
    className?: string;
}

function QueryResultCard({
    query,
    result,
    queryTitle = "Query",
    resultTitle = "Result",
    defaultExpanded = false,
    timestamp,
    className,
}: QueryResultCardProps) {
    const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);
    const [copiedQuery, setCopiedQuery] = React.useState(false);
    const [copiedResult, setCopiedResult] = React.useState(false);

    // 复制到剪贴板
    const copyToClipboard = (text: string, setCopied: (v: boolean) => void) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // 获取可复制的文本
    const getTextContent = (content: React.ReactNode): string => {
        if (typeof content === "string") return content;
        if (React.isValidElement(content)) {
            const props = content.props as Record<string, any>;
            return props.children?.toString() || "";
        }
        return String(content);
    };

    const queryText = getTextContent(query);
    const resultText = getTextContent(result);

    return (
        <div className={cn("w-full", className)}>
            <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden" role="region" aria-label="Query result card">
                {/* Header */}
                <div className="flex items-center justify-between gap-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white px-4 py-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                            <h3 className="text-sm font-semibold text-gray-900 truncate">
                                {queryTitle}
                            </h3>
                        </div>
                        {timestamp && (
                            <p className="mt-1 text-xs text-gray-500">{timestamp}</p>
                        )}
                    </div>
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className={cn(
                            "shrink-0 rounded-lg p-2 transition-all duration-200",
                            "hover:bg-gray-100 active:scale-95"
                        )}
                        aria-label={isExpanded ? "Collapse result" : "Expand result"}
                    >
                        <ChevronDown className={cn(
                            "h-5 w-5 text-gray-600 transition-transform duration-300",
                            isExpanded && "rotate-180"
                        )} />
                    </button>
                </div>

                {/* Query Section */}
                <div className="relative bg-gray-50 p-4 border-b border-gray-200">
                    <div className="flex items-start justify-between gap-2 mb-2">
                        <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                            参数
                        </p>
                        <button
                            onClick={() => copyToClipboard(queryText, setCopiedQuery)}
                            className="p-1 rounded hover:bg-gray-200 transition-colors"
                            title="复制参数"
                        >
                            {copiedQuery ? (
                                <Check className="h-4 w-4 text-green-600" />
                            ) : (
                                <Copy className="h-4 w-4 text-gray-500" />
                            )}
                        </button>
                    </div>
                    <div className="text-sm whitespace-pre-wrap break-words font-mono text-gray-900 bg-white rounded p-3 border border-gray-200 max-h-48 overflow-y-auto">
                        {typeof query === "string" ? query : query}
                    </div>
                </div>

                {/* Result Section - Collapsible */}
                <AnimatePresence>
                    {isExpanded && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="overflow-hidden"
                        >
                            <div className="relative bg-blue-50 p-4 border-t border-gray-200">
                                <div className="flex items-start justify-between gap-2 mb-2">
                                    <p className="text-xs font-medium text-blue-700 uppercase tracking-wide">
                                        {resultTitle}
                                    </p>
                                    <button
                                        onClick={() => copyToClipboard(resultText, setCopiedResult)}
                                        className="p-1 rounded hover:bg-blue-200 transition-colors"
                                        title="复制结果"
                                    >
                                        {copiedResult ? (
                                            <Check className="h-4 w-4 text-green-600" />
                                        ) : (
                                            <Copy className="h-4 w-4 text-blue-600" />
                                        )}
                                    </button>
                                </div>
                                <div className="text-sm text-gray-900 bg-white rounded p-3 border border-blue-200 max-h-96 overflow-y-auto">
                                    {typeof result === "string" ? (
                                        <p className="whitespace-pre-wrap break-words font-mono">{result}</p>
                                    ) : (
                                        result
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Expand Button */}
                {!isExpanded && (
                    <motion.button
                        onClick={() => setIsExpanded(true)}
                        className={cn(
                            "w-full text-sm font-medium py-3 px-4",
                            "flex items-center justify-center gap-2",
                            "bg-gradient-to-r from-blue-50 to-blue-50 hover:from-blue-100 hover:to-blue-100",
                            "border-t border-gray-200 text-blue-700 transition-all duration-200",
                            "hover:shadow-md group"
                        )}
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                    >
                        <Sparkles className="h-4 w-4" />
                        <span>查看结果</span>
                        <ChevronDown className="h-4 w-4 group-hover:translate-y-0.5 transition-transform" />
                    </motion.button>
                )}
            </div>
        </div>
    );
}

export { QueryResultCard, type QueryResultCardProps };

