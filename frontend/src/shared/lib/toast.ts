
import { toast as shadcnToast } from "@/shared/hooks/use-toast"

export const toast = {
  error: (title: string, description?: string) =>
    shadcnToast({ title, description, variant: "destructive", duration: 3000 }),

  info: (title: string, description?: string) =>
    shadcnToast({ title, description, variant: "default", duration: 3000 }),
}
