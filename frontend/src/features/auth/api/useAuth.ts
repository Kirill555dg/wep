import { useMutation } from '@tanstack/react-query'
import { loginApiV1AuthLoginPost, registerApiV1AuthRegisterPost, type LoginRequest, type UserCreate } from '@/shared/api'
import { client } from '@/shared/api/generated/client.gen'

export function useLogin() {
  return useMutation({
    mutationFn: (body: LoginRequest) => loginApiV1AuthLoginPost({ client, body }),
  })
}

export function useRegister() {
  return useMutation({
    mutationFn: (body: UserCreate) => registerApiV1AuthRegisterPost({ client, body }),
  })
}
