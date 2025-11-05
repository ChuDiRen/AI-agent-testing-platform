/**
 * Next.js Image 组件的 Vite 兼容版本
 * 在 Vite 环境中，我们直接使用标准的 img 标签
 */
import React from 'react';

export default function Image({ src, alt, width, height, className, priority, ...props }) {
  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      loading={priority ? 'eager' : 'lazy'}
      {...props}
    />
  );
}

