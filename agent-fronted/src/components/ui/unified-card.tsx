import * as React from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader } from "./card";

// 统一卡片容器组件 # 确保所有卡片样式一致
interface UnifiedCardProps extends React.ComponentProps<typeof Card> {
  children: React.ReactNode;
  header?: React.ReactNode;
  variant?: "default" | "elevated" | "bordered";
  size?: "sm" | "md" | "lg";
}

export function UnifiedCard({
  children,
  header,
  variant = "default",
  size = "md",
  className,
  ...props
}: UnifiedCardProps) {
  // 尺寸映射 # 统一的尺寸系统
  const sizeClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  // 变体样式 # 不同的视觉风格
  const variantClasses = {
    default: "border border-gray-200 bg-white shadow-sm",
    elevated: "border-0 bg-white shadow-md hover:shadow-lg transition-shadow duration-300",
    bordered: "border-2 border-gray-300 bg-white shadow-none",
  };

  return (
    <Card
      className={cn(
        "w-full rounded-xl transition-all duration-200",
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {header && (
        <CardHeader className={cn("border-b border-gray-100", sizeClasses[size])}>
          {header}
        </CardHeader>
      )}
      <CardContent className={cn(header ? "pt-6" : "", sizeClasses[size])}>
        {children}
      </CardContent>
    </Card>
  );
}

// 卡片容器组 # 用于包裹多个卡片
interface CardContainerProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
  spacing?: "tight" | "normal" | "relaxed";
}

export function CardContainer({
  children,
  className,
  maxWidth = "2xl",
  spacing = "normal",
}: CardContainerProps) {
  // 最大宽度映射 # 响应式宽度控制
  const maxWidthClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
    full: "max-w-full",
  };

  // 间距映射 # 统一的间距系统
  const spacingClasses = {
    tight: "gap-3",
    normal: "gap-4",
    relaxed: "gap-6",
  };

  return (
    <div
      className={cn(
        "mx-auto flex w-full flex-col",
        maxWidthClasses[maxWidth],
        spacingClasses[spacing],
        className
      )}
    >
      {children}
    </div>
  );
}

