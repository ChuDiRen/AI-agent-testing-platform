import React from 'react';
import { Hexagon } from 'lucide-react';

interface LogoProps {
  className?: string;
  size?: number;
}

export const Logo: React.FC<LogoProps> = ({ className = "", size = 32 }) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="relative flex items-center justify-center text-primary">
        <Hexagon size={size} strokeWidth={2.5} className="fill-blue-100" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-primary rounded-full" />
        </div>
      </div>
      <span className="font-bold text-xl tracking-tight text-slate-900 font-sans">
        NEXUS<span className="text-primary">.OS</span>
      </span>
    </div>
  );
};
