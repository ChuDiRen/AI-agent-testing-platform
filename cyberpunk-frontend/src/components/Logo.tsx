import React from 'react';
import { Hexagon } from 'lucide-react';

interface LogoProps {
  className?: string;
  size?: number;
}

export const Logo: React.FC<LogoProps> = ({ className = "", size = 32 }) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="relative flex items-center justify-center text-neon-purple">
        <Hexagon size={size} strokeWidth={2.5} className="text-neon-purple drop-shadow-[0_0_8px_rgba(188,19,254,0.6)]" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-pulse shadow-[0_0_10px_rgba(0,243,255,0.8)]" />
        </div>
      </div>
      <span className="font-bold text-xl tracking-tight text-white font-display cyber-text-glow">
        NEXUS<span className="text-neon-cyan">.OS</span>
      </span>
    </div>
  );
};

