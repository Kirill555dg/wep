import { useState } from 'react'
import { loginApiV1AuthLoginPost, registerApiV1AuthRegisterPost } from '@/shared/api'
import { client } from '@/shared/api/generated/client.gen'

export function useLogin() {
  const [isLoading, setIsLoading] = useState(false)

  const mutate = async (data: { username_or_email: string; password: string }) => {
    try {
      setIsLoading(true)
      const response = await loginApiV1AuthLoginPost({ client, body: data })
      const result = response.data as any
      if (result?.access_token) {
        localStorage.setItem('access_token', result.access_token)
      }
      return result
    } finally {
      setIsLoading(false)
    }
  }

  return { mutate, isLoading, isPending: isLoading }
}

export function useRegister() {
  const [isLoading, setIsLoading] = useState(false)

  const mutate = async (data: any) => {
    try {
      setIsLoading(true)
      await registerApiV1AuthRegisterPost({ client, body: data })
    } finally {
      setIsLoading(false)
    }
  }

  return { mutate, isLoading, isPending: isLoading }
}
