import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

interface CyberCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  icon?: React.ElementType;
  extra?: React.ReactNode;
  delay?: number;
  hoverEffect?: boolean;
}

export const CyberCard: React.FC<CyberCardProps> = ({ 
  children, 
  className = "", 
  title, 
  icon: Icon, 
  extra,
  delay = 0,
  hoverEffect = true
}) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={cn(
        "bg-slate-900/60 backdrop-blur-xl border border-slate-800/60 rounded-xl p-6 flex flex-col relative overflow-hidden group",
        hoverEffect && "hover:border-neon-cyan/30 hover:shadow-[0_0_15px_rgba(0,243,255,0.1)] transition-all duration-300",
        className
      )}
    >
      {/* Decorative Corner Accents */}
      <div className="absolute top-0 left-0 w-2 h-2 border-l border-t border-slate-700 group-hover:border-neon-cyan transition-colors" />
      <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-slate-700 group-hover:border-neon-cyan transition-colors" />
      <div className="absolute bottom-0 left-0 w-2 h-2 border-l border-b border-slate-700 group-hover:border-neon-cyan transition-colors" />
      <div className="absolute bottom-0 right-0 w-2 h-2 border-r border-b border-slate-700 group-hover:border-neon-cyan transition-colors" />

      {(title || Icon) && (
        <div className="flex items-center justify-between mb-4 z-10 relative">
          <div className="flex items-center gap-2 text-slate-100 font-medium">
            {Icon && (
              <div className="p-1.5 rounded-lg bg-slate-800/50 text-neon-cyan group-hover:text-white group-hover:bg-neon-cyan transition-colors">
                <Icon size={18} />
              </div>
            )}
            <span className="text-lg tracking-tight group-hover:text-neon-cyan transition-colors">{title}</span>
          </div>
          {extra}
        </div>
      )}
      <div className="flex-1 min-h-0 relative z-10">
        {children}
      </div>
      
      {/* Background Gradient Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
    </motion.div>
  );
};
