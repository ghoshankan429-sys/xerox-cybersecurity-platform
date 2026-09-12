import React from "react";
import { Link } from "react-router-dom";

export interface NavigationItemProps {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  isActive: boolean;
  badge?: string | number;
  collapsed?: boolean;
  onClick?: () => void;
}

export const NavigationItem: React.FC<NavigationItemProps> = ({
  href,
  icon: Icon,
  label,
  isActive,
  badge,
  collapsed = false,
  onClick,
}) => {
  return (
    <Link
      to={href}
      onClick={onClick}
      title={collapsed ? label : undefined}
      className={`group relative flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-mono tracking-wide transition-all duration-200 outline-none focus-visible:ring-2 focus-visible:ring-xerox-red ${
        isActive
          ? "bg-xerox-red/15 text-red-400 border border-xerox-red/30 shadow-[0_0_15px_rgba(239,68,68,0.18)]"
          : "text-slate-400 hover:text-slate-200 hover:bg-xerox-surface border border-transparent"
      }`}
    >
      {/* Active Indicator Bar */}
      {isActive && (
        <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-xerox-red shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
      )}

      <Icon
        className={`w-4 h-4 flex-shrink-0 transition-transform group-hover:scale-105 ${
          isActive ? "text-xerox-red" : "text-slate-400 group-hover:text-slate-200"
        }`}
      />

      {!collapsed && (
        <div className="flex-1 flex items-center justify-between overflow-hidden">
          <span className="truncate">{label}</span>
          {badge !== undefined && (
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded font-mono font-bold border ${
                isActive
                  ? "bg-xerox-red/20 text-red-300 border-red-500/30"
                  : "bg-slate-800 text-slate-400 border-slate-700"
              }`}
            >
              {badge}
            </span>
          )}
        </div>
      )}
    </Link>
  );
};
