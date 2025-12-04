"use client";

import { FC, useState } from "react";
import { cn } from "@/lib/utils";
import { ImageIcon, XIcon } from "lucide-react";

interface MarkdownImageProps {
  src?: string;
  alt?: string;
  className?: string;
}

export const MarkdownImage: FC<MarkdownImageProps> = ({
  src,
  alt = "图片",
  className
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const handleLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  const handleImageClick = () => {
    if (!hasError) {
      setIsPreviewOpen(true);
    }
  };

  const handleClosePreview = () => {
    setIsPreviewOpen(false);
  };

  if (!src) {
    return null;
  }

  return (
    <>
      <span className={cn("my-4 relative inline-block max-w-full", className)}>
        {isLoading && !hasError && (
          <span className="flex items-center justify-center min-h-[200px] bg-muted rounded-lg border inline-flex">
            <span className="flex flex-col items-center gap-2 text-muted-foreground">
              <ImageIcon className="h-8 w-8 animate-pulse" />
              <span className="text-sm">加载中...</span>
            </span>
          </span>
        )}

        {hasError && (
          <span className="flex items-center justify-center min-h-[200px] bg-muted rounded-lg border inline-flex">
            <span className="flex flex-col items-center gap-2 text-muted-foreground max-w-md px-4">
              <ImageIcon className="h-8 w-8" />
              <span className="text-sm">图片加载失败</span>
              {alt && <span className="text-xs text-muted-foreground/70">{alt}</span>}
              <a
                href={src}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-blue-500 hover:underline truncate max-w-full"
              >
                点击查看原图
              </a>
            </span>
          </span>
        )}

        <img
          src={src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          onClick={handleImageClick}
          className={cn(
            "max-w-full rounded-lg border shadow-sm transition-opacity",
            isLoading || hasError ? "hidden" : "inline-block",
            !hasError && "cursor-pointer hover:opacity-90 hover:shadow-md"
          )}
        />
      </span>

      {/* 图片预览弹窗 */}
      {isPreviewOpen && !hasError && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={handleClosePreview}
        >
          <button
            className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
            onClick={handleClosePreview}
          >
            <XIcon className="h-6 w-6 text-white" />
          </button>
          <img
            src={src}
            alt={alt}
            className="max-w-full max-h-full object-contain rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
};

