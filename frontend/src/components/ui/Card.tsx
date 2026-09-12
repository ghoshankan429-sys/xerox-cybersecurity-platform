import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "interactive" | "alert";
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant = "default",
  className = "",
  children,
  ...props
}) => {
  const variantStyles = {
    default: "bg-xerox-surface border-xerox-border",
    elevated: "bg-xerox-surface-elevated border-xerox-border-highlight shadow-panel",
    interactive:
      "bg-xerox-surface border-xerox-border hover:border-slate-500 hover:bg-xerox-surface-elevated transition-all duration-200 cursor-pointer hover:shadow-panel active:scale-[0.99]",
    alert:
      "bg-xerox-surface border-red-500/30 shadow-[0_0_25px_rgba(239,68,68,0.15)]",
  };

  return (
    <div
      className={`rounded-2xl border p-5 sm:p-6 relative overflow-hidden ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className = "",
  children,
  ...props
}) => (
  <div className={`flex flex-col space-y-1.5 pb-4 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  className = "",
  children,
  ...props
}) => (
  <h3
    className={`text-base sm:text-lg font-bold text-slate-100 tracking-tight flex items-center gap-2 ${className}`}
    {...props}
  >
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  className = "",
  children,
  ...props
}) => (
  <p className={`text-xs text-slate-400 font-sans leading-relaxed ${className}`} {...props}>
    {children}
  </p>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className = "",
  children,
  ...props
}) => (
  <div className={`space-y-4 ${className}`} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className = "",
  children,
  ...props
}) => (
  <div className={`flex items-center justify-between pt-4 border-t border-xerox-border-subtle ${className}`} {...props}>
    {children}
  </div>
);
