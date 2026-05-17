import {toast as baseToast} from "@/shared/hooks/use-toast";

export function toast(opts: {title?: string; description?: string; variant?: "default" | "destructive"}) {
  baseToast({...opts});
}
