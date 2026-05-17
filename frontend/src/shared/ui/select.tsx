/**
 * Minimal select wrapper using native select with Tailwind styling.
 */
import {forwardRef, SelectHTMLAttributes} from 'react'
import {cn} from '@/shared/lib/utils'

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(({className, children, ...props}, ref) => (
  <select ref={ref} className={cn('flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2', className)} {...props}>
    {children}
  </select>
))
Select.displayName = 'Select'

export const SelectItem = forwardRef<HTMLOptionElement, React.OptionHTMLAttributes<HTMLOptionElement>>(({className, children, ...props}, ref) => (
  <option ref={ref} className={cn('py-1', className)} {...props}>
    {children}
  </option>
))
SelectItem.displayName = 'SelectItem'

export const SelectContent = ({children}: {children: React.ReactNode}) => <>{children}</>
export const SelectTrigger = ({children}: {children: React.ReactNode}) => <>{children}</>
export const SelectValue = ({placeholder}: {placeholder?: string}) => <span className="text-muted-foreground">{placeholder}</span>
