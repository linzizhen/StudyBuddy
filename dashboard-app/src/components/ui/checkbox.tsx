import * as React from "react"
import { cn } from "@/lib/utils"

export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        type="checkbox"
        ref={ref}
        className={cn(
          "w-4 h-4 rounded border-2 border-slate-300 text-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 cursor-pointer accent-emerald-500",
          className
        )}
        {...props}
      />
    )
  }
)
Checkbox.displayName = "Checkbox"

export { Checkbox }
