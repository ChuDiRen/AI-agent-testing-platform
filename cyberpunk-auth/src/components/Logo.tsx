import React from 'react';
import { Hexagon } from 'lucide-react';

interface LogoProps {
  className?: string;
  size?: number;
}

export const Logo: React.FC<LogoProps> = ({ className = "", size = 32 }) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="relative flex items-center justify-center text-indigo-500">
        <Hexagon size={size} strokeWidth={2.5} className="text-indigo-500" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.8)]" />
        </div>
      </div>
      <span className="font-bold text-xl tracking-tight text-white font-mono">
        NEXUS<span className="text-cyan-400">.OS</span>
      </span>
    </div>
  );
};
