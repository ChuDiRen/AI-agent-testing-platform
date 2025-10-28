import * as React from "react";
import { ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./card";
import { Button } from "./button";

interface QueryResultCardProps extends React.ComponentProps<typeof Card> {
    query: React.ReactNode;
    result: React.ReactNode;
    queryTitle?: React.ReactNode;
    resultTitle?: React.ReactNode;
    defaultExpanded?: boolean;
    timestamp?: string;
}

function QueryResultCard({
    query,
    result,
    queryTitle = "Query",
    resultTitle = "Result",
    defaultExpanded = false,
    timestamp,
    className,
    ...props
}: QueryResultCardProps) {
    const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);
    const [isHovered, setIsHovered] = React.useState(false);

    return (
        <Card
            className={cn(
                "w-full relative overflow-hidden transition-all duration-300",
                "hover:shadow-xl hover:scale-[1.01]",
                "border-2 border-transparent hover:border-primary/20",
                "bg-gradient-to-br from-card via-card to-card/95",
                className
            )}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            {...props}
        >
            {/* Animated gradient background */}
            <div className={cn(
                "absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-blue-500/5 opacity-0 transition-opacity duration-500",
                isHovered && "opacity-100"
            )} />

            {/* Sparkle effect on hover */}
            <div className={cn(
                "absolute top-4 right-4 transition-all duration-500",
                isHovered ? "opacity-100 scale-100" : "opacity-0 scale-50"
            )}>
                <Sparkles className="size-4 text-primary/40 animate-pulse" />
            </div>

            <CardHeader className="relative">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                        <CardTitle className={cn(
                            "text-lg font-semibold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text transition-all duration-300",
                            isHovered && "from-primary to-primary/70"
                        )}>
                            {queryTitle}
                        </CardTitle>
                        {timestamp && (
                            <CardDescription className="mt-1 text-xs">{timestamp}</CardDescription>
                        )}
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setIsExpanded(!isExpanded)}
                        className={cn(
                            "shrink-0 rounded-full transition-all duration-300",
                            "hover:bg-primary/10 hover:scale-110",
                            isExpanded && "rotate-180"
                        )}
                        aria-label={isExpanded ? "Collapse result" : "Expand result"}
                    >
                        <ChevronDown className={cn(
                            "size-5 transition-all duration-300",
                            isExpanded && "text-primary"
                        )} />
                    </Button>
                </div>
            </CardHeader>

            <CardContent className="space-y-4 relative">
                {/* Query Section */}
                <div className={cn(
                    "rounded-xl p-4 transition-all duration-300 relative overflow-hidden",
                    "bg-gradient-to-br from-muted/50 to-muted/30",
                    "border border-border/50",
                    "hover:border-primary/30 hover:shadow-md"
                )}>
                    {/* Decorative corner */}
                    <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-primary/10 to-transparent rounded-bl-full" />

                    <p className="text-xs text-muted-foreground mb-3 font-semibold uppercase tracking-wide flex items-center gap-2">
                        <span className="w-1 h-4 bg-gradient-to-b from-primary to-primary/50 rounded-full" />
                        Query
                    </p>
                    <div className="text-sm whitespace-pre-wrap break-words font-mono relative z-10">
                        {typeof query === "string" ? query : query}
                    </div>
                </div>

                {/* Result Section - Collapsible */}
                <div
                    className={cn(
                        "overflow-hidden transition-all duration-500 ease-in-out",
                        isExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0",
                    )}
                >
                    <div className={cn(
                        "rounded-xl p-4 transition-all duration-300 relative overflow-hidden",
                        "bg-gradient-to-br from-primary/5 via-card to-blue-500/5",
                        "border-2 border-primary/20",
                        "shadow-inner"
                    )}>
                        {/* Animated gradient line */}
                        <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-primary to-transparent animate-pulse" />

                        <p className="text-xs text-muted-foreground mb-3 font-semibold uppercase tracking-wide flex items-center gap-2">
                            <span className="w-1 h-4 bg-gradient-to-b from-green-500 to-green-500/50 rounded-full" />
                            {resultTitle}
                        </p>
                        <div className="text-sm relative z-10">
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
                            "bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10",
                            "hover:from-primary/20 hover:via-primary/10 hover:to-primary/20",
                            "border border-primary/20 hover:border-primary/40",
                            "text-primary transition-all duration-300",
                            "hover:shadow-lg hover:scale-[1.02]",
                            "group"
                        )}
                    >
                        <Sparkles className="size-4 opacity-70 group-hover:opacity-100 transition-opacity" />
                        <span>Show Result</span>
                        <ChevronDown className="size-4 group-hover:translate-y-0.5 transition-transform" />
                    </button>
                )}
            </CardContent>
        </Card>
    );
}

export { QueryResultCard, type QueryResultCardProps };

