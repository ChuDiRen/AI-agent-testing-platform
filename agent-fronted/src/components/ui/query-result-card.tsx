import * as React from "react";
import { ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { UnifiedCard } from "./unified-card"; // 使用统一卡片组件

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

    return (
        <UnifiedCard variant="bordered" size="md" className={className}>
            <div className="flex w-full flex-col gap-4">
                {/* Header with expand button */}
                <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                        <h3 className="text-base font-semibold text-gray-900">
                            {queryTitle}
                        </h3>
                        {timestamp && (
                            <p className="mt-1 text-xs text-gray-500">{timestamp}</p>
                        )}
                    </div>
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className={cn(
                            "shrink-0 rounded-full p-2 transition-all duration-200",
                            "hover:bg-gray-100",
                            isExpanded && "rotate-180"
                        )}
                        aria-label={isExpanded ? "Collapse result" : "Expand result"}
                    >
                        <ChevronDown className={cn(
                            "h-5 w-5 text-gray-600 transition-colors",
                            isExpanded && "text-blue-600"
                        )} />
                    </button>
                </div>

                {/* Query Section */}
                <div className="rounded-lg bg-gray-50 p-4 border border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-2 uppercase tracking-wide">
                        Query
                    </p>
                    <div className="text-sm whitespace-pre-wrap break-words font-mono text-gray-900">
                        {typeof query === "string" ? query : query}
                    </div>
                </div>

                {/* Result Section - Collapsible */}
                <div
                    className={cn(
                        "overflow-hidden transition-all duration-300 ease-in-out",
                        isExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0",
                    )}
                >
                    <div className="rounded-lg bg-blue-50 p-4 border-2 border-blue-200">
                        <p className="text-xs font-medium text-blue-700 mb-2 uppercase tracking-wide">
                            {resultTitle}
                        </p>
                        <div className="text-sm text-gray-900">
                            {typeof result === "string" ? (
                                <p className="whitespace-pre-wrap break-words font-mono">{result}</p>
                            ) : (
                                result
                            )}
                        </div>
                    </div>
                </div>

                {/* Expand/Collapse Button at Bottom */}
                {!isExpanded && (
                    <button
                        onClick={() => setIsExpanded(true)}
                        className={cn(
                            "w-full text-sm font-medium py-3 px-4 rounded-lg",
                            "flex items-center justify-center gap-2",
                            "bg-blue-50 hover:bg-blue-100",
                            "border border-blue-200 hover:border-blue-300",
                            "text-blue-700 transition-all duration-200",
                            "hover:shadow-md",
                            "group"
                        )}
                    >
                        <Sparkles className="h-4 w-4" />
                        <span>Show Result</span>
                        <ChevronDown className="h-4 w-4 group-hover:translate-y-0.5 transition-transform" />
                    </button>
                )}
            </div>
        </UnifiedCard>
    );
}

export { QueryResultCard, type QueryResultCardProps };

