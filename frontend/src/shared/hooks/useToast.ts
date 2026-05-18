import { useMemo } from 'react'
import toast, {ToastOptions, ToastPosition} from 'react-hot-toast'

const defaultOptions: ToastOptions = {
  position: 'top-right' as ToastPosition,
  duration: 3000,
  style: {
    background: '#1a1a1a',
    color: '#fff',
    padding: '16px',
    borderRadius: '8px',
    fontSize: '14px',
  },
}

export function useToast() {
  return useMemo(() => {
    const success = (message: string, options?: ToastOptions) => {
      toast.success(message, {...defaultOptions, ...options})
    }

    const error = (message: string, options?: ToastOptions) => {
      toast.error(message, {
        ...defaultOptions,
        style: {
          ...defaultOptions.style,
          background: '#ef4444',
        },
        ...options,
      })
    }

    const info = (message: string, options?: ToastOptions) => {
      toast(message, {...defaultOptions, ...options})
    }

    const loading = (message: string, options?: ToastOptions) => {
      return toast.loading(message, {
        ...defaultOptions,
        duration: Infinity,
        ...options,
      })
    }

    const dismiss = (id: string) => {
      toast.dismiss(id)
    }

    return {
      success,
      error,
      info,
      loading,
      dismiss,
    }
  }, [])
}
